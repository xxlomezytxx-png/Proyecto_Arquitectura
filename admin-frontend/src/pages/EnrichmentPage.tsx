import { useCallback, useState } from "react";
import { uploadExcel, UploadResult } from "../services/enrichmentService";
import styles from "./EnrichmentPage.module.css";

type UploadState = "idle" | "uploading" | "done" | "error";

const EnrichmentPage = () => {
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [result, setResult] = useState<UploadResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleFile = async (file: File) => {
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      setErrorMsg("Solo se permiten archivos Excel (.xlsx, .xls)");
      setUploadState("error");
      return;
    }
    setFileName(file.name);
    setUploadState("uploading");
    setErrorMsg("");
    setResult(null);
    try {
      const data = await uploadExcel(file);
      setResult(data);
      setUploadState("done");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al subir el archivo";
      setErrorMsg(msg);
      setUploadState("error");
    }
  };

  const onFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }, []);

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const onDragLeave = () => setDragging(false);

  const reset = () => {
    setUploadState("idle");
    setResult(null);
    setErrorMsg("");
    setFileName("");
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Enriquecimiento de Catálogo</h1>
        <p className={styles.subtitle}>
          Carga un archivo Excel con ISBN, título y datos del libro para enriquecer el catálogo comercial.
        </p>
      </div>

      <div className={styles.instructions}>
        <h3>Columnas esperadas en el Excel</h3>
        <div className={styles.columns}>
          {["ISBN 13", "ISBN 10", "ISSN", "Título del libro", "URL PORTADA", "Estado del libro", "unidades disponibles"].map(col => (
            <span key={col} className={styles.colBadge}>{col}</span>
          ))}
        </div>
      </div>

      <div
        className={`${styles.dropZone} ${dragging ? styles.dragging : ""} ${uploadState === "done" ? styles.success : ""}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        {uploadState === "idle" && (
          <>
            <div className={styles.dropIcon}>📂</div>
            <p className={styles.dropText}>Arrastra tu archivo Excel aquí</p>
            <p className={styles.dropSub}>o</p>
            <label className={styles.browseBtn}>
              Seleccionar archivo
              <input type="file" accept=".xlsx,.xls" onChange={onFileInput} hidden />
            </label>
          </>
        )}

        {uploadState === "uploading" && (
          <>
            <div className={styles.spinner} />
            <p className={styles.dropText}>Procesando {fileName}…</p>
          </>
        )}

        {uploadState === "done" && result && (
          <>
            <div className={styles.dropIcon}>✅</div>
            <p className={styles.dropText}>Carga completada</p>
            <p className={styles.dropSub}>{fileName}</p>
          </>
        )}

        {uploadState === "error" && (
          <>
            <div className={styles.dropIcon}>❌</div>
            <p className={styles.dropText}>Error al procesar</p>
            <p className={styles.errorText}>{errorMsg}</p>
          </>
        )}
      </div>

      {(uploadState === "done" || uploadState === "error") && (
        <button className={styles.resetBtn} onClick={reset}>
          Cargar otro archivo
        </button>
      )}

      {uploadState === "done" && result && (
        <div className={styles.results}>
          <div className={styles.kpiRow}>
            <div className={`${styles.kpi} ${styles.kpiGreen}`}>
              <span className={styles.kpiNum}>{result.inserted ?? 0}</span>
              <span className={styles.kpiLabel}>Insertados</span>
            </div>
            <div className={`${styles.kpi} ${styles.kpiYellow}`}>
              <span className={styles.kpiNum}>{result.duplicated ?? 0}</span>
              <span className={styles.kpiLabel}>Duplicados</span>
            </div>
            <div className={`${styles.kpi} ${styles.kpiRed}`}>
              <span className={styles.kpiNum}>{result.errors ?? 0}</span>
              <span className={styles.kpiLabel}>Errores</span>
            </div>
            <div className={`${styles.kpi} ${styles.kpiBlue}`}>
              <span className={styles.kpiNum}>{result.total_rows_processed ?? 0}</span>
              <span className={styles.kpiLabel}>Total filas</span>
            </div>
          </div>

          {result.inserted > 0 && (
            <div className={styles.table}>
              <h4 className={styles.tableTitle}>✅ Libros insertados ({result.inserted})</h4>
              <ul className={styles.list}>
                {result.inserted_preview.map((item, i) => (
                  <li key={i} className={styles.listItemGreen}>{item.title}</li>
                ))}
              </ul>
            </div>
          )}

          {result.duplicated > 0 && (
            <div className={styles.table}>
              <h4 className={styles.tableTitle}>⚠️ Duplicados ({result.duplicated})</h4>
              <ul className={styles.list}>
                {result.duplicated_preview.map((item, i) => (
                  <li key={i} className={styles.listItemYellow}>{item.title}</li>
                ))}
              </ul>
            </div>
          )}

          {result.errors > 0 && (
            <div className={styles.table}>
              <h4 className={styles.tableTitle}>❌ Errores ({result.errors})</h4>
              <ul className={styles.list}>
                {result.error_preview.map((item, i) => (
                  <li key={i} className={styles.listItemRed}>
                    {item.title ?? item.isbn ?? `Fila ${item.row}`}
                    {" — "}
                    {typeof item.error === "string" ? item.error : JSON.stringify(item.error)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnrichmentPage;
