"""Genera el documento del modelo y los diagramas a partir de modelo.toml.

Uso:
    python docs/diseno/generar.py

Si la variable de entorno PLANTUML_JAR apunta a plantuml.jar, también
convierte los diagramas UML a PNG en docs/diseno/img/. Hace falta Java y Graphviz.

Si la variable EDGE apunta a msedge.exe (o Edge está en su ruta de siempre),
convierte también los BPMN a PNG con bpmn-js. Necesita internet, porque
bpmn-js se carga desde su CDN.
"""
import json
import os
import subprocess
import tempfile
import tomllib
from pathlib import Path

import bpmn

AQUI = Path(__file__).parent
IMG = AQUI / "img"

# El estilo de los diagramas UML está en estilo.iuml, que comparten los
# diagramas generados y los escritos a mano.
ESTILO = "!include estilo.iuml"


def cargar():
    with open(AQUI / "modelo.toml", "rb") as f:
        return tomllib.load(f)


def nombres(m, clave):
    return {x["id"]: x["nombre"] for x in m[clave]}


def documento(m):
    """Escribe modelo.md: las tablas de actores, casos de uso y entidades."""
    actores = nombres(m, "actor")
    modulos = nombres(m, "modulo")
    casos = nombres(m, "caso")

    lineas = [
        f"# Modelo del sistema {m['sistema']['nombre']}",
        "",
        "Este archivo se genera desde `modelo.toml`. Para cambiar algo, se edita ese archivo y se vuelve a correr `generar.py`.",
        "",
        "## Actores",
        "",
        "| Actor | Descripción |",
        "|---|---|",
    ]
    for a in m["actor"]:
        nombre = a["nombre"] + (" (abstracto)" if a.get("abstracto") else "")
        lineas.append(f"| {nombre} | {a['descripcion']} |")

    for mod_id, mod_nombre in modulos.items():
        lineas += ["", f"## Casos de uso: {mod_nombre}", "", "| Código | Caso de uso | Actor | Descripción |", "|---|---|---|---|"]
        for c in m["caso"]:
            if c["modulo"] != mod_id:
                continue
            quien = ", ".join(actores[a] for a in c["actores"]) or "El sistema"
            desc = c["descripcion"]
            if c.get("incluye"):
                desc += " Incluye: " + ", ".join(f"{i} {casos[i]}" for i in c["incluye"]) + "."
            lineas.append(f"| {c['id']} | {c['nombre']} | {quien} | {desc} |")

    lineas += ["", "## Entidades", ""]
    for e in m["entidad"]:
        lineas += [f"### {e['nombre']}", "", e["descripcion"], ""]
        lineas += [f"- {at}" for at in e["atributos"]]
        lineas.append("")

    (AQUI / "modelo.md").write_text("\n".join(lineas), encoding="utf-8")
    return "modelo.md"


def casos_de_uso(m):
    """Escribe casos-de-uso.puml: el diagrama general, un paquete por módulo."""
    orden = m["diagrama"]["casos_de_uso"]
    actores = {a["id"]: a for a in m["actor"]}
    modulos = {x["id"]: x for x in m["modulo"]}

    lineas = ["@startuml casos-de-uso", ESTILO, "left to right direction",
              "skinparam nodesep 16", "skinparam ranksep 60", ""]

    # El orden de declaración decide dónde cae cada cosa en el dibujo.
    for aid in orden["actores"]:
        a = actores[aid]
        estereotipo = " <<abstracto>>" if a.get("abstracto") else ""
        lineas.append(f'actor "{a["nombre"]}" as {aid}{estereotipo}')
    lineas.append("")

    lineas.append(f'rectangle "{m["sistema"]["nombre"]}" {{')
    for mid in orden["paquetes"]:
        lineas.append(f'  package "{modulos[mid]["nombre"]}" {{')
        for c in m["caso"]:
            if c["modulo"] == mid:
                lineas.append(f'    usecase "{c["nombre"]}" as {c["id"]}')
        lineas.append("  }")
    lineas += ["}", ""]

    # Escrita así, la herencia deja al actor abstracto a la izquierda de todos.
    for aid in orden["actores"]:
        if actores[aid].get("generaliza"):
            lineas.append(f"{actores[aid]['generaliza']} <|-- {aid}")
    for c in m["caso"]:
        for a in c["actores"]:
            lineas.append(f"{a} --> {c['id']}")
    for c in m["caso"]:
        for i in c.get("incluye", []):
            lineas.append(f"{c['id']} ..> {i} : <<include>>")

    lineas.append("@enduml")
    (AQUI / "casos-de-uso.puml").write_text("\n".join(lineas), encoding="utf-8")
    return "casos-de-uso.puml"


def a_png(archivos):
    """Convierte los .puml a PNG si hay PlantUML disponible."""
    jar = os.environ.get("PLANTUML_JAR")
    if not jar:
        return []
    IMG.mkdir(exist_ok=True)
    rutas = [str(AQUI / a) for a in archivos]
    subprocess.run(["java", "-jar", jar, "-tpng", "-Sdpi=170", "-o", str(IMG), *rutas], check=True)
    return [Path(a).with_suffix(".png").name for a in archivos]


EDGE_POR_DEFECTO = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

PAGINA_BPMN = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;background:#fff;overflow:hidden}} #c{{width:{w}px;height:{h}px}}</style>
<script src="https://cdn.jsdelivr.net/npm/bpmn-js@17/dist/bpmn-viewer.production.min.js"></script>
</head><body><div id="c"></div><script>
const v = new BpmnJS({{ container: '#c' }});
v.importXML({xml}).then(() => v.get('canvas').viewbox({{ x: 0, y: 0, width: {w}, height: {h} }}));
</script></body></html>"""


def bpmn_a_png(hechos):
    """Dibuja cada .bpmn con bpmn-js en Edge sin ventana y guarda la captura."""
    edge = os.environ.get("EDGE", EDGE_POR_DEFECTO)
    if not Path(edge).exists():
        return []
    IMG.mkdir(exist_ok=True)
    salida = []
    for nombre, (w, h) in hechos:
        xml = (AQUI / nombre).read_text(encoding="utf-8")
        pagina = Path(tempfile.mkdtemp()) / "bpmn.html"
        pagina.write_text(PAGINA_BPMN.format(w=w, h=h, xml=json.dumps(xml)), encoding="utf-8")
        png = IMG / nombre.replace(".bpmn", ".png")
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", "--force-device-scale-factor=2",
                        "--virtual-time-budget=20000", f"--screenshot={png}", pagina.as_uri()],
                       capture_output=True, timeout=120)
        if png.exists():
            salida.append(png.name)
    return salida


if __name__ == "__main__":
    m = cargar()
    hechos = [documento(m), casos_de_uso(m)]
    procesos = bpmn.generar()
    print("generado:", ", ".join(hechos + [p for p, _ in procesos]))
    # Se convierten todos los .puml de la carpeta: los generados y los escritos a mano.
    pumls = sorted(p.name for p in AQUI.glob("*.puml"))
    imagenes = a_png(pumls) + bpmn_a_png(procesos)
    if imagenes:
        print("imágenes:", ", ".join(imagenes))
