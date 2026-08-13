function StatCard({ item }) {
  return (
    <article className="stat-card">
      <span className="stat-card-marker" aria-hidden="true" />
      <p>{item.label}</p>
    </article>
  )
}

export default StatCard
