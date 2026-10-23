"""Genera el documento del modelo y los diagramas a partir de modelo.toml.

Uso:
    python docs/diseno/generar.py
"""
import tomllib
from pathlib import Path

AQUI = Path(__file__).parent


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


if __name__ == "__main__":
    m = cargar()
    print("generado:", documento(m))
