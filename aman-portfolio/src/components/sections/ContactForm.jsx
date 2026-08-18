import { useEffect, useRef, useState } from 'react'

const initialValues = { name: '', email: '', subject: '', message: '' }
const recipient = 'amankaushik2810@gmail.com'

function validateForm(values) {
  const errors = {}
  if (values.name.length < 2) errors.name = 'Enter a name with at least 2 characters.'
  if (!values.email) errors.email = 'Enter your email address.'
  else if (!/^\S+@\S+\.\S+$/.test(values.email)) errors.email = 'Enter a valid email address.'
  if (values.subject.length < 3) errors.subject = 'Enter a subject with at least 3 characters.'
  if (values.message.length < 10) errors.message = 'Enter a message with at least 10 characters.'
  return errors
}

function ContactForm() {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [status, setStatus] = useState('')
  const [isPreparing, setIsPreparing] = useState(false)
  const fieldsRef = useRef({})
  const resetTimerRef = useRef(null)
  useEffect(() => () => window.clearTimeout(resetTimerRef.current), [])
  const update = (name, value) => setValues((current) => ({ ...current, [name]: value }))
  const handleSubmit = (event) => {
    event.preventDefault()
    if (isPreparing) return
    const trimmed = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value.trim()]))
    const nextErrors = validateForm(trimmed)
    setErrors(nextErrors)
    setStatus('')
    if (Object.keys(nextErrors).length) { fieldsRef.current[Object.keys(nextErrors)[0]]?.focus(); return }
    setIsPreparing(true)
    const body = ['Hello Aman,', '', trimmed.message, '', 'Sender details:', `Name: ${trimmed.name}`, `Email: ${trimmed.email}`].join('\n')
    const params = new URLSearchParams({ view: 'cm', fs: '1', to: recipient, su: trimmed.subject, body })
    const gmailWindow = window.open(`https://mail.google.com/mail/?${params.toString()}`, '_blank')
    if (gmailWindow) {
      try { gmailWindow.opener = null } catch { /* The new window has already navigated cross-origin. */ }
      setStatus('Gmail opened with your message prepared.')
    } else {
      window.location.assign(`mailto:${recipient}?subject=${encodeURIComponent(trimmed.subject)}&body=${encodeURIComponent(body)}`)
      setStatus('Your default mail client was opened with your message prepared.')
    }
    resetTimerRef.current = window.setTimeout(() => setIsPreparing(false), 800)
  }
  return <form className="contact-form" noValidate onSubmit={handleSubmit}><div className="grid gap-5 sm:grid-cols-2"><Field fieldRef={fieldsRef} errors={errors} label="Name" name="name" onChange={update} value={values.name}/><Field fieldRef={fieldsRef} errors={errors} label="Email" name="email" type="email" onChange={update} value={values.email}/></div><Field fieldRef={fieldsRef} errors={errors} label="Subject" name="subject" onChange={update} value={values.subject}/><Field fieldRef={fieldsRef} errors={errors} label="Message" name="message" textarea onChange={update} value={values.message}/><button className="contact-submit" type="submit" disabled={isPreparing}>Prepare Email <span aria-hidden="true">{'\u2709'}</span></button><p className="contact-form-helper">This will open Gmail with your message prepared. Review it and press Send.</p>{status && <p className="contact-form-status" aria-live="polite">{status}</p>}</form>
}
function Field({ errors, fieldRef, label, name, onChange, textarea = false, type = 'text', value }) { const id = `contact-${name}`; const error = errors[name]; const props = { ref: (node) => { fieldRef.current[name] = node }, id, name, type, value, 'aria-invalid': Boolean(error), 'aria-describedby': error ? `${id}-error` : undefined, onChange: (event) => onChange(name, event.target.value) }; return <div className="contact-field"><label htmlFor={id}>{label}</label>{textarea ? <textarea rows="5" {...props}/> : <input {...props}/>} {error && <p id={`${id}-error`} role="alert">{error}</p>}</div> }
export default ContactForm
