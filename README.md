# empleo_publico_es
Aid for Spanish Public Employment candidates.

Ayuda para candidatos al empleo público en sector público de España.

## Resumen

El repositorio incluye:

1. _/data/raw_ : Documentación original de convocatorias de empleo en la ruta.
2. _/data/processed/_ : Datos de convocatorias disponibles en formatos procesables (texto plano, ficheros semiestructurados como XML, tablas, etc.).
3. _/src/_ : Aplicaciones para generar o transformar datos procesados a partir de los PDFs o para preparar los ejercicios.

## Documentación de convocatorias

Se recopila la documentación original de las convocatorias públicas que se distribuye únicamente en PDF.

La estructura de carpetas es:

/data/raw/<num_cuerpo>/<año_convocatoria>

* _<num_cuerpo>_ es el código de cuerpo. Ejemplo: 1188. Los códigos de cuerpos se pueden consultar en el fichero [/data/cuerpos.csv](https://github.com/pmgallardo/empleo_publico_es/blob/main/data/cuerpos.csv)
* _<año_convocatoria>_ es el año de la convocatoria. Ejemplo: 2022

## Datos de convocatorias procesables

Se almacena datos derivados de la documentación original en formatos fácilmente procesables (como texto plano, tablas o XML).

El tipo de material encontrado puede ser:
* temario: títulos del temario
* test: preguntas de tests

La estructura de las carpetas es:

/data/processed/<num_cuerpo>/<tipo_material>/<ref_temporal>

* _<num_cuerpo>_ es el código de cuerpo. Ejemplo: 1188. Los códigos de cuerpos se pueden consultar en el fichero [/data/cuerpos.csv](https://github.com/pmgallardo/empleo_publico_es/blob/main/data/cuerpos.csv)
* _<tipo_material>_ es el tipo de material ofrecido para las convocatorias de ese cuerpo. Pueden ser títulos del temario (temario) o preguntas de test (test).
* _<ref_temporal>_ es una referencia temporal, que puede ser el año de convocatoria (ejemplo: 2022) o una fecha en formato yyyymmdd (ejemplo: 20230606)

## Aplicaciones

El código fuente de las aplicaciones se encuentra en la ruta /src

### Quiz CLI

**Quiz CLI** es una aplicación para terminal para realizar preguntas de cuestionario.

### doc_tools

Aplicaciones que han ayudado a generar los datos procesados.