const pdfQaPipeline = ['PDF Upload', 'Text Extraction', 'Chunking', 'Embeddings', 'FAISS Retrieval', 'Ollama Answer']

function ProjectArchitecture({ architecture }) {
  if (architecture?.type === 'pdf-qa-rag') {
    return (
      <div className="project-architecture" aria-label="PDF QA RAG Assistant pipeline">
        {pdfQaPipeline.map((step, index) => (
          <div className="pipeline-step" key={step}>
            <span>{step}</span>
            {index < pdfQaPipeline.length - 1 && <i aria-hidden="true">→</i>}
          </div>
        ))}
      </div>
    )
  }

  return <p className="case-study-placeholder">Architecture/workflow: {architecture?.placeholder || 'CASE_STUDY_ARCHITECTURE_TO_BE_ADDED'}</p>
}

export default ProjectArchitecture
