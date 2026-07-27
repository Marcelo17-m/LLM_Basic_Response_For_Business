# data/

Colocá acá tus documentos fuente:

- `sales.csv` (o el nombre que configures en `CSV_PATH`): datos tabulares (ventas, métricas, etc.)
- `policies.pdf` (o el nombre que configures en `PDF_PATH`): documento en texto (políticas, manual, documentación técnica)

Si tus documentos contienen información sensible o confidencial, agregalos a `.gitignore`
antes de hacer commit para no publicarlos en el repositorio público.

La carpeta `faiss_index/` se genera automáticamente la primera vez que se indexa el PDF;
no hace falta crearla ni tocarla a mano.
