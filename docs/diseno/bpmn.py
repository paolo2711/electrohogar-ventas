"""Arma los archivos BPMN 2.0 a partir de procesos.toml.

Escribe el XML con su diagrama (posiciones de carriles, tareas y flechas), así
que el .bpmn se abre tal cual en bpmn.io o en Camunda Modeler.
"""
import tomllib
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

AQUI = Path(__file__).parent

COL_W = 162          # ancho de cada columna
CARRIL_H = 170       # alto de cada carril
POOL_X, POOL_Y = 20, 20
BANDA = 30           # franja del nombre del proceso y de cada carril
X0 = POOL_X + 2 * BANDA + 20

TAMANO = {
    "tarea": (132, 82), "manual": (132, 82), "usuario": (132, 82), "servicio": (132, 82),
    "inicio": (36, 36), "inicio_tiempo": (36, 36), "fin": (36, 36),
    "compuerta": (50, 50),
}
ETIQUETA_BPMN = {
    "tarea": "task", "manual": "manualTask", "usuario": "userTask", "servicio": "serviceTask",
    "inicio": "startEvent", "inicio_tiempo": "startEvent", "fin": "endEvent",
    "compuerta": "exclusiveGateway",
}


class Caja:
    def __init__(self, nodo, fila):
        self.n = nodo
        self.tipo = nodo["tipo"]
        self.w, self.h = TAMANO[self.tipo]
        self.cx = X0 + nodo["columna"] * COL_W + COL_W / 2
        self.cy = POOL_Y + fila * CARRIL_H + CARRIL_H / 2 + nodo.get("dy", 0)
        self.x, self.y = self.cx - self.w / 2, self.cy - self.h / 2

    @property
    def izq(self): return self.x
    @property
    def der(self): return self.x + self.w
    @property
    def arriba(self): return self.y
    @property
    def abajo(self): return self.y + self.h


def ruta(s, t):
    """Puntos de una flecha en ángulo recto, de la caja s a la caja t."""
    if abs(s.cy - t.cy) < 1:
        return [(s.der, s.cy), (t.izq, t.cy)]
    baja = t.cy > s.cy
    if abs(s.cx - t.cx) < 1:
        return [(s.cx, s.abajo if baja else s.arriba), (t.cx, t.arriba if baja else t.abajo)]
    if s.tipo == "compuerta":
        # De una compuerta, la rama sale por arriba o por abajo y luego va a la derecha.
        return [(s.cx, s.abajo if baja else s.arriba), (s.cx, t.cy), (t.izq, t.cy)]
    xm = (s.der + t.izq) / 2
    return [(s.der, s.cy), (xm, s.cy), (xm, t.cy), (t.izq, t.cy)]


def bounds(x, y, w, h):
    return f'<dc:Bounds x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" />'


def armar(p):
    pid = p["id"].replace("-", "_")
    filas = {c["id"]: i for i, c in enumerate(p["carriles"])}
    cajas = {n["id"]: Caja(n, filas[n["carril"]]) for n in p["nodos"]}
    ncols = max(n["columna"] for n in p["nodos"]) + 1
    pool_w = (X0 - POOL_X) + ncols * COL_W + 20
    pool_h = len(p["carriles"]) * CARRIL_H

    entra = {n: [] for n in cajas}
    sale = {n: [] for n in cajas}
    flujos = []
    for i, f in enumerate(p["flujos"], 1):
        fid = f"Flujo_{pid}_{i}"
        sale[f["de"]].append(fid)
        entra[f["a"]].append(fid)
        flujos.append((fid, f))

    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" '
         'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
         'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" '
         'xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
         f'id="Def_{pid}" targetNamespace="https://github.com/paolo2711/electrohogar-ventas">',
         f'  <bpmn:collaboration id="Colab_{pid}">',
         f'    <bpmn:participant id="Part_{pid}" name={quoteattr(p["nombre"])} processRef="Proc_{pid}" />',
         '  </bpmn:collaboration>',
         f'  <bpmn:process id="Proc_{pid}" isExecutable="false">',
         f'    <bpmn:laneSet id="Carriles_{pid}">']
    for c in p["carriles"]:
        x.append(f'      <bpmn:lane id="Carril_{pid}_{c["id"]}" name={quoteattr(c["nombre"])}>')
        for n in p["nodos"]:
            if n["carril"] == c["id"]:
                x.append(f'        <bpmn:flowNodeRef>{pid}_{n["id"]}</bpmn:flowNodeRef>')
        x.append('      </bpmn:lane>')
    x.append('    </bpmn:laneSet>')

    for n in p["nodos"]:
        tag = ETIQUETA_BPMN[n["tipo"]]
        x.append(f'    <bpmn:{tag} id="{pid}_{n["id"]}" name={quoteattr(n["nombre"])}>')
        for fid in entra[n["id"]]:
            x.append(f'      <bpmn:incoming>{fid}</bpmn:incoming>')
        for fid in sale[n["id"]]:
            x.append(f'      <bpmn:outgoing>{fid}</bpmn:outgoing>')
        if n["tipo"] == "inicio_tiempo":
            x.append(f'      <bpmn:timerEventDefinition id="Tiempo_{pid}_{n["id"]}" />')
        x.append(f'    </bpmn:{tag}>')
    for fid, f in flujos:
        nombre = f' name={quoteattr(f["nombre"])}' if f.get("nombre") else ""
        x.append(f'    <bpmn:sequenceFlow id="{fid}" sourceRef="{pid}_{f["de"]}" targetRef="{pid}_{f["a"]}"{nombre} />')
    x.append('  </bpmn:process>')

    # Diagrama
    x += [f'  <bpmndi:BPMNDiagram id="Diagrama_{pid}">',
          f'    <bpmndi:BPMNPlane id="Plano_{pid}" bpmnElement="Colab_{pid}">',
          f'      <bpmndi:BPMNShape id="Part_{pid}_di" bpmnElement="Part_{pid}" isHorizontal="true">',
          f'        {bounds(POOL_X, POOL_Y, pool_w, pool_h)}',
          '      </bpmndi:BPMNShape>']
    for i, c in enumerate(p["carriles"]):
        x += [f'      <bpmndi:BPMNShape id="Carril_{pid}_{c["id"]}_di" bpmnElement="Carril_{pid}_{c["id"]}" isHorizontal="true">',
              f'        {bounds(POOL_X + BANDA, POOL_Y + i * CARRIL_H, pool_w - BANDA, CARRIL_H)}',
              '      </bpmndi:BPMNShape>']
    for n in p["nodos"]:
        b = cajas[n["id"]]
        extra = ' isMarkerVisible="true"' if n["tipo"] == "compuerta" else ""
        x += [f'      <bpmndi:BPMNShape id="{pid}_{n["id"]}_di" bpmnElement="{pid}_{n["id"]}"{extra}>',
              f'        {bounds(b.x, b.y, b.w, b.h)}']
        if n["tipo"] in ("inicio", "inicio_tiempo", "fin"):
            if n.get("etiqueta") == "derecha":
                lb = bounds(b.der + 6, b.cy - 9, 110, 18)
            else:
                lb = bounds(b.cx - 55, b.abajo + 4, 110, 28)
            x.append(f'        <bpmndi:BPMNLabel>{lb}</bpmndi:BPMNLabel>')
        elif n["tipo"] == "compuerta":
            # Si una rama sale hacia arriba, la etiqueta va abajo para que la flecha no la cruce.
            sube = any(cajas[f["a"]].cy < b.cy - 1 for _, f in flujos if f["de"] == n["id"])
            y = b.abajo + 4 if sube else b.arriba - 34
            x.append(f'        <bpmndi:BPMNLabel>{bounds(b.cx - 65, y, 130, 28)}</bpmndi:BPMNLabel>')
        x.append('      </bpmndi:BPMNShape>')

    for fid, f in flujos:
        pts = ruta(cajas[f["de"]], cajas[f["a"]])
        x.append(f'      <bpmndi:BPMNEdge id="{fid}_di" bpmnElement="{fid}">')
        for px, py in pts:
            x.append(f'        <di:waypoint x="{px:.0f}" y="{py:.0f}" />')
        if f.get("nombre"):
            (x1, y1), (x2, y2) = pts[0], pts[1]
            if abs(x1 - x2) < 1:
                lb = bounds(x1 + 5, (y1 + y2) / 2 - 8, 24, 16)
            else:
                lb = bounds(x1 + 6, y1 - 20, 24, 16)
            x.append(f'        <bpmndi:BPMNLabel>{lb}</bpmndi:BPMNLabel>')
        x.append('      </bpmndi:BPMNEdge>')
    x += ['    </bpmndi:BPMNPlane>', '  </bpmndi:BPMNDiagram>', '</bpmn:definitions>', '']

    tam = (POOL_X * 2 + pool_w, POOL_Y * 2 + pool_h)
    return "\n".join(x), tam


def generar():
    """Escribe un .bpmn por proceso. Devuelve [(archivo, (ancho, alto))]."""
    with open(AQUI / "procesos.toml", "rb") as f:
        procesos = tomllib.load(f)["proceso"]
    hechos = []
    for p in procesos:
        xml, tam = armar(p)
        nombre = f"{p['id']}.bpmn"
        (AQUI / nombre).write_text(xml, encoding="utf-8")
        hechos.append((nombre, tam))
    return hechos
