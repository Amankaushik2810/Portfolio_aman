function SectionHeading({ eyebrow, title, description, titleId }) {
  return (
    <header className="max-w-2xl">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h2 className="mt-4 font-display text-[clamp(2rem,4vw,3.5rem)] font-semibold leading-[1.08] tracking-[-0.05em] text-balance" id={titleId}>
        {title}
      </h2>
      {description && <p className="mt-5 max-w-xl text-base leading-7 text-portfolio-muted sm:text-lg">{description}</p>}
    </header>
  )
}

export default SectionHeading
