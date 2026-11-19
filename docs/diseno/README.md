# Diseño del sistema

Aquí vive el diseño de ElectroHogar Ventas: los actores, los casos de uso de cada módulo, los procesos de negocio y los diagramas que salen de ellos.

Los diagramas se escriben como código (PlantUML para UML y BPMN 2.0 para los procesos de negocio), así que cada cambio queda versionado y se puede revisar en una pull request como cualquier otro archivo.

## Modelo de datos

`datos.py` lee los modelos de Django y escribe en `datos/` los cuatro niveles del modelo de la base de datos: conceptual (notación de Chen), diagrama de clases, lógico y físico, más `esquema.sql` con el SQL de PostgreSQL. No necesita un servidor de PostgreSQL.

```
python docs/diseno/datos.py
```

Con `PLANTUML_JAR` apuntando a `plantuml.jar` también deja los PNG en `img/`. Una prueba revisa que `esquema.sql` coincida con los modelos, así que si se cambia un modelo y no se regenera, el CI falla.

## Componentes y secuencias

`componentes.puml` muestra las piezas del sistema y cómo se conectan (navegador, apps de Django, base de datos y GitHub). En `secuencias/` están los diagramas de secuencia de los flujos principales: inicio de sesión, venta y cobro, ingreso de mercadería y anulación. Se escriben a mano siguiendo el código, y se convierten con `java -jar plantuml.jar -tpng -o img componentes.puml secuencias/*.puml`.
