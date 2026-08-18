const pdfQaPipeline = ['PDF Upload', 'Text Extraction', 'Chunking', 'Embeddings', 'FAISS Retrieval', 'Ollama Answer']

function WorkflowIcon({ name }) {
  const common = { fill: 'none', stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '1.7' }
  const icons = {
    user: <><circle cx="12" cy="8" r="3" {...common} /><path d="M5.5 19c.8-3 3-4.7 6.5-4.7s5.7 1.7 6.5 4.7" {...common} /></>,
    phone: <><rect x="7.5" y="3.5" width="9" height="17" rx="1.5" {...common} /><path d="M10.5 17.5h3" {...common} /></>,
    lock: <><rect x="5.5" y="10" width="13" height="10" rx="1.7" {...common} /><path d="M8.5 10V7.5a3.5 3.5 0 0 1 7 0V10" {...common} /></>,
    pen: <><path d="m6 18 1.2-4.3L16.6 4.3a1.8 1.8 0 0 1 2.5 2.5l-9.4 9.4L6 18Z" {...common} /><path d="m14.8 6.1 3.1 3.1" {...common} /></>,
    shield: <><path d="M12 3.7 19 6v5.2c0 4.5-2.8 7.4-7 9.1-4.2-1.7-7-4.6-7-9.1V6l7-2.3Z" {...common} /><path d="m9 11.9 2 2 4-4.2" {...common} /></>,
    book: <><path d="M5 5.5c2.8-1 5.2-.7 7 1.1 1.8-1.8 4.2-2.1 7-1.1v13c-2.8-1-5.2-.7-7 1.1-1.8-1.8-4.2-2.1-7-1.1v-13Z" {...common} /><path d="M12 6.6v13" {...common} /></>,
    heart: <path d="M12 19.2 5.5 13c-2.1-2.1-.6-5.8 2.4-5.8 1.7 0 3 1 4.1 2.5 1.1-1.5 2.4-2.5 4.1-2.5 3 0 4.5 3.7 2.4 5.8L12 19.2Z" {...common} />,
    bell: <><path d="M6.5 16.5h11l-1.3-2.1v-4a4.2 4.2 0 0 0-8.4 0v4l-1.3 2.1Z" {...common} /><path d="M10 19a2.2 2.2 0 0 0 4 0" {...common} /></>,
  }
  return <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24">{icons[name]}</svg>
}

function PoeticPebblesWorkflow({ architecture }) {
  return (
    <div className="pp-architecture mt-5">
      <div className="pp-architecture-shell rounded-3xl p-4 sm:p-6">
        <div className="pp-body space-y-4 text-sm leading-7">
          {architecture.description.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        </div>

        <ol aria-label="Poetic Pebbles publishing workflow" className="mt-7 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {architecture.steps.map(([title, description, icon], index) => (
            <li className={`pp-workflow-node pp-workflow-node-${index} relative min-h-32 rounded-2xl p-4`} key={title}>
              <div className="flex items-center gap-3">
                <span className="pp-node-number flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold">{index + 1}</span>
                <span className="pp-node-icon flex h-8 w-8 items-center justify-center rounded-full"><WorkflowIcon name={icon} /></span>
              </div>
              <h4 className="pp-card-heading mt-4 text-sm font-semibold">{title}</h4>
              <p className="pp-body mt-1.5 text-xs leading-5">{description}</p>
              {index < architecture.steps.length - 1 && <span className="pp-vertical-connector absolute -bottom-3 left-7 z-10 h-3 border-l xl:hidden" aria-hidden="true" />}
              {index < architecture.steps.length - 1 && <span className="pp-desktop-connector absolute -right-3 top-10 hidden xl:block" aria-hidden="true">→</span>}
            </li>
          ))}
        </ol>

        <div className="mt-7 grid gap-4 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="pp-services-panel rounded-2xl p-4">
            <h4 className="pp-card-heading text-sm font-semibold">Supporting services</h4>
            <ul className="mt-3 grid gap-2 sm:grid-cols-2">
              {architecture.services.map((service) => <li className="pp-service-item rounded-xl px-3 py-2 text-xs font-medium" key={service}>{service}</li>)}
            </ul>
          </div>
          <aside className="pp-ai-panel relative rounded-2xl p-4">
            <span className="pp-ai-badge inline-flex rounded-full px-2.5 py-1 text-[0.68rem] font-bold uppercase tracking-[0.12em]">In development</span>
            <h4 className="pp-card-heading mt-3 text-sm font-semibold">Poetic Pebbles AI</h4>
            <p className="pp-body mt-2 text-xs leading-5">{architecture.future}</p>
          </aside>
        </div>
      </div>

      <div className="pp-complete-workflow mt-5 rounded-2xl p-5">
        <h4 className="pp-card-heading text-sm font-semibold">Complete workflow</h4>
        <ol className="pp-workflow-list mt-4 space-y-3 pl-5">
          {architecture.workflow.map((step, index) => <li className="pp-body relative text-sm leading-6" key={step}><span className="pp-list-number absolute -left-[1.95rem] top-0 flex h-5 w-5 items-center justify-center rounded-full text-[0.62rem] font-bold">{index + 1}</span>{step}</li>)}
        </ol>
      </div>
    </div>
  )
}

const hiresenseInputs = ['CSV candidate dataset', 'Text-based PDF resume', 'Manually entered resume text']
const preprocessing = ['Clean and normalize resume text', 'Remove duplicate records', 'Handle missing values', 'Calculate resume length', 'Derive experience level', 'Extract candidate name', 'Extract skills', 'Extract education', 'Extract experience']
const mlSteps = ['Random Forest shortlist classifier', 'Logistic Regression baseline', 'Random Forest/Gradient Boosting match-score experimentation', 'Model evaluation', 'EDA and model visualizations']
const ragSteps = ['TF-IDF keyword analysis', 'Skill-frequency analysis', 'Candidate knowledge base', 'TF-IDF vectorization', 'Cosine-similarity retrieval', 'Top-five relevant candidates']
const appViews = ['Dashboard', 'Resume Screening', 'RAG Search', 'Candidate Insights', 'Model Evaluation']
const llmOutputs = ['Professional resume summary', 'Job-description generation', 'Resume-to-job match analysis', 'Interview questions when match score exceeds 75%', 'Advisory final recommendation']

function FlowIcon({ type }) {
  const props = { fill: 'none', stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '1.7' }
  const paths = {
    input: <><path d="M5 5.5h14v13H5z" {...props} /><path d="M8 9h8M8 13h5" {...props} /></>,
    process: <><path d="M12 3.5v3M12 17.5v3M3.5 12h3M17.5 12h3M6 6l2.1 2.1M15.9 15.9 18 18M18 6l-2.1 2.1M8.1 15.9 6 18" {...props} /><circle cx="12" cy="12" r="3.7" {...props} /></>,
    model: <><path d="M5 17.5V10m7 7.5V6m7 11.5v-4" {...props} /><path d="M3.5 19.5h17" {...props} /></>,
    search: <><circle cx="10.5" cy="10.5" r="5.5" {...props} /><path d="m15 15 4.2 4.2" {...props} /></>,
    app: <><rect x="4" y="4" width="16" height="16" rx="2" {...props} /><path d="M4 9h16M9 9v11" {...props} /></>,
    llm: <><path d="M7 5.5h10a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-5l-3.7 2.7.7-2.7H7a3 3 0 0 1-3-3v-5a3 3 0 0 1 3-3Z" {...props} /><path d="M9 11h.01M12 11h.01M15 11h.01" {...props} /></>,
    human: <><circle cx="12" cy="8" r="3" {...props} /><path d="M5 20c.8-3.6 3.2-5.5 7-5.5s6.2 1.9 7 5.5" {...props} /><path d="m16.5 15.5 1.2 1.2 2.3-2.4" {...props} /></>,
  }
  return <svg aria-hidden="true" viewBox="0 0 24 24">{paths[type]}</svg>
}

function ListNode({ title, items, icon, tone = '' }) {
  return <article className={`hs-flow-node ${tone}`}><div className="hs-flow-node-heading"><span><FlowIcon type={icon} /></span><h4>{title}</h4></div><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></article>
}

function DownConnector({ label }) {
  return <div className="hs-down-connector" aria-hidden="true"><span>{label}</span><i>↓</i></div>
}

function HireSenseWorkflow() {
  return <div className="hs-architecture" aria-label="HireSense AI architecture and recruiter-support workflow">
    <section className="hs-arch-stage"><div className="hs-stage-label"><span>1</span><h4>Inputs</h4></div><div className="hs-flow-stage hs-flow-input"><ListNode title="Input Sources" items={hiresenseInputs} icon="input" /></div></section>
    <DownConnector label="Normalize" />
    <section className="hs-arch-stage"><div className="hs-stage-label"><span>2</span><h4>Processing</h4></div><div className="hs-flow-stage"><ListNode title="Resume Parsing and Data Processing" items={preprocessing} icon="process" tone="hs-flow-process" /></div></section>
    <DownConnector label="Enrich" />
    <section className="hs-arch-stage"><div className="hs-stage-label"><span>3</span><h4>Intelligence pipelines</h4></div><div className="hs-branches" aria-label="Parallel machine learning and NLP RAG branches"><ListNode title="Machine Learning" items={mlSteps} icon="model" tone="hs-flow-ml" /><ListNode title="NLP and RAG" items={ragSteps} icon="search" tone="hs-flow-rag" /><p className="hs-validation-note">Regression validation being improved</p></div></section>
    <DownConnector label="Merge insights" />
    <section className="hs-arch-stage hs-arch-workspace"><div className="hs-stage-label"><span>4</span><h4>Streamlit workspace</h4></div><div className="hs-flow-stage"><ListNode title="Streamlit Application" items={appViews} icon="app" tone="hs-flow-app" /><ListNode title="Local Llama 3.2 via Ollama" items={['Local assistance for summaries, generation and analysis']} icon="llm" tone="hs-flow-llm" /></div></section>
    <DownConnector label="Advisory output" />
    <section className="hs-arch-stage hs-arch-output"><div className="hs-stage-label"><span>5</span><h4>Recruiter-facing output</h4></div><div className="hs-flow-stage"><ListNode title="Recruiter-facing insights" items={llmOutputs} icon="llm" tone="hs-flow-llm" /><ListNode title="Recruiter review and final human decision" items={['Evidence-led, advisory support — never an autonomous hiring decision']} icon="human" tone="hs-flow-human" /></div></section>
  </div>
}

function KaushikFootprintsWorkflow() {
  const customer = ['Customer Storefront', 'React Application', 'Product, authentication and cart requests']
  const api = ['Node.js + Express REST API', 'Product services', 'Authentication services', 'Protected cart operations', 'Image upload and delivery']
  const admin = ['Admin Panel', 'React Application', 'Upload product image', 'Add product', 'View product catalogue', 'Remove product']
  return <div className="kf-architecture" aria-label="Kaushik’s Footprints customer, admin, API and data workflow">
    <div className="kf-architecture-grid"><article className="kf-arch-node kf-arch-customer"><span>Customer layer</span>{customer.map((item) => <p key={item}>{item}</p>)}</article><i aria-hidden="true">↓</i><article className="kf-arch-node kf-arch-api"><span>API layer</span>{api.map((item) => <p key={item}>{item}</p>)}</article><i aria-hidden="true">↓</i><article className="kf-arch-node kf-arch-data"><span>Data and storage layer</span><p>MongoDB</p><p>Products · Users · Cart Data</p></article></div>
    <div className="kf-admin-flow"><article className="kf-arch-node kf-arch-admin"><span>Admin layer</span>{admin.map((item) => <p key={item}>{item}</p>)}</article><i aria-hidden="true">↓</i><article className="kf-arch-node kf-arch-api"><span>Shared API layer</span><p>Server image storage</p><p>MongoDB product collection</p></article><i aria-hidden="true">↓</i><article className="kf-arch-result"><span>Updated products appear in the customer storefront</span></article></div>
  </div>
}

function ProjectArchitecture({ architecture }) {
  if (architecture?.type === 'poetic-pebbles-workflow') return <PoeticPebblesWorkflow architecture={architecture} />
  if (architecture?.type === 'hiresense-workflow') return <HireSenseWorkflow />
  if (architecture?.type === 'kaushik-footprints-workflow') return <KaushikFootprintsWorkflow />

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

  return <p className="case-study-placeholder">Architecture/workflow: {architecture?.placeholder || 'Workflow details are being prepared.'}</p>
}

export default ProjectArchitecture
