"""Genera el documento del modelo y los diagramas a partir de modelo.toml.

Uso:
    python docs/diseno/generar.py

Si la variable de entorno PLANTUML_JAR apunta a plantuml.jar, también
convierte los diagramas a PNG en docs/diseno/img/. Hace falta Java y Graphviz.
"""
import os
import subprocess
import tomllib
from pathlib import Path

AQUI = Path(__file__).parent
IMG = AQUI / "img"

# Estilo común de todos los diagramas UML: blanco y negro, Arial, sin sombras.
ESTILO = """skinparam defaultFontName Arial
skinparam defaultFontSize 13
skinparam shadowing false
skinparam backgroundColor #FFFFFF
skinparam ArrowColor #333333
skinparam ArrowThickness 1
skinparam actorBorderColor #222222
skinparam actorBackgroundColor #FFFFFF
skinparam usecaseBorderColor #333333
skinparam usecaseBackgroundColor #FFFFFF
skinparam packageBorderColor #888888
skinparam packageBackgroundColor #F7F7F7
skinparam packageFontStyle bold
skinparam rectangleBorderColor #222222
skinparam rectangleFontStyle bold"""


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


if __name__ == "__main__":
    m = cargar()
    hechos = [documento(m), casos_de_uso(m)]
    print("generado:", ", ".join(hechos))
    imagenes = a_png([h for h in hechos if h.endswith(".puml")])
    if imagenes:
        print("imágenes:", ", ".join(imagenes))
