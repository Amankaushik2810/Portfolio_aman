import ProjectArchitecture from './ProjectArchitecture.jsx'
import ProjectLinks from './ProjectLinks.jsx'

const technologies = [
  ['React', 'Creates the responsive customer storefront, reusable interface components, category pages, product views and cart experience.'],
  ['Node.js', 'Provides the server-side JavaScript runtime used to execute the application backend.'],
  ['Express', 'Handles REST endpoints for products, authentication, cart operations and image uploads.'],
  ['MongoDB', 'Persists product information, user records and user-specific cart data.'],
  ['JWT', 'Supports token-based authenticated requests for user-specific operations.'],
  ['Multer', 'Processes product-image uploads from the admin interface.'],
]

const features = [
  ['Product discovery', 'Customers can explore products through the main storefront and category-specific pages for men, women and kids.'],
  ['Product details', 'Each product can be opened on a dedicated page containing its image, category and pricing information.'],
  ['User authentication', 'Signup and login workflows allow the backend to identify users and issue JWT tokens for authenticated operations.'],
  ['Persistent cart management', 'Cart quantities are connected to the authenticated user and stored in MongoDB instead of existing only in temporary frontend state.'],
  ['Cart calculation', 'The frontend calculates product quantities, item totals and the combined cart amount.'],
  ['Catalogue administration', 'A separate admin application enables product creation, catalogue listing and product removal.'],
  ['Product-image upload', 'The admin can upload product images through the Express backend, which stores and serves them to the application.'],
  ['Shared product data', 'The customer storefront and admin panel operate on the same product collection, creating a connected catalogue workflow.'],
]

const challenges = [
  ['Connecting multiple application layers', 'The customer storefront, admin interface and backend run as separate modules. Their API URLs, request formats and expected responses had to remain consistent so that all parts of the application could communicate correctly.'],
  ['Managing CORS and local development ports', 'Because the frontend, admin interface and backend can run on different local ports, cross-origin API communication required proper CORS configuration and consistent backend endpoints.'],
  ['Creating user-specific cart persistence', 'Cart state could not be treated as a single global collection. Each authenticated user needed an independent cart that could be retrieved and updated through protected API requests.'],
  ['Maintaining authentication state', 'The frontend needed to store and attach the JWT token to protected requests. Login, signup and cart operations had to follow a consistent authentication flow.'],
  ['Handling product images', 'Image uploads introduced a different data flow from ordinary JSON requests. The backend needed to accept multipart uploads, store the files and return accessible image paths to the admin interface and storefront.'],
  ['Synchronising catalogue data', 'Products created or removed from the admin interface needed to remain consistent with what customers received from the product APIs.'],
  ['Organising separate storefront and admin modules', 'The application required different routes, components and interactions for customers and administrators. Keeping those responsibilities separated helped prevent the codebase from becoming one tightly coupled interface.'],
  ['Preparing the application for production', 'Moving from local development to production requires environment-based API URLs, protected secrets, password hashing, restricted administrative endpoints, upload validation, production CORS policies and complete checkout handling.'],
]

const lessons = [
  ['Full-stack features depend on end-to-end coordination', 'A feature is not complete only because its interface exists. Frontend state, API behavior, database models and error handling must all agree on the same data structure and workflow.'],
  ['Persistent state changes application design', 'Moving cart information from temporary frontend state into MongoDB makes the experience user-specific, but also introduces authentication, database updates and synchronisation requirements.'],
  ['Authentication must be applied consistently', 'Token-based authentication requires more than issuing a JWT. Protected requests must send the token correctly, and the backend must verify it before accessing user-specific information.'],
  ['Media handling requires its own workflow', 'Product images require multipart uploads, file storage, public delivery paths and validation. This makes image management an important backend responsibility.'],
  ['Separate interfaces benefit from shared APIs', 'The storefront and admin panel serve different users, but both become easier to manage when they use the same backend services and product database.'],
  ['Modular architecture improves maintainability', 'Separating customer components, administrative components, routes, API logic and database models makes the application easier to understand and extend.'],
  ['Production readiness goes beyond feature development', 'A production application also needs environment variables, secret management, password hashing, protected admin routes, input validation, testing, monitoring and reliable deployment configuration.'],
]

const future = ['Complete and verify order persistence.', 'Integrate a production-ready payment gateway.', 'Add admin order-management capabilities.', 'Add product search, sorting and advanced filtering.', 'Add stock and inventory tracking.', 'Add wishlist functionality.', 'Add customer order history.', 'Add verified promo-code handling.', 'Add image type, size and upload validation.', 'Move all API addresses and sensitive configuration into environment variables.', 'Hash passwords and strengthen authentication handling.', 'Protect administrative endpoints using role-based authorization.', 'Add automated frontend and backend tests.', 'Deploy the storefront, admin panel, backend and database using production configuration.']

function Section({ title, children, tone = '' }) { return <section className={`kf-section ${tone}`}><h3>{title}</h3>{children}</section> }

function KaushikFootprintsCaseStudy({ project }) {
  return <div className="kf-case-study">
    <section className="kf-hero" aria-label="Kaushik’s Footprints overview"><p>FULL-STACK E-COMMERCE CASE STUDY</p><h2 id="project-modal-title">Kaushik’s Footprints</h2><h3>Building a connected fashion and lifestyle shopping experience with React, Express and MongoDB.</h3><div className="kf-hero-copy"><p id="project-modal-overview">Kaushik’s Footprints is a full-stack e-commerce application designed for a fashion and lifestyle store. It combines a responsive customer storefront, a REST-based backend, persistent MongoDB data and a separate admin interface for managing products and product images.</p><p>The application demonstrates how customer-facing shopping workflows and administrative catalogue operations can be connected through a shared backend and database.</p></div><dl className="kf-metadata"><div><dt>Type</dt><dd>Full-Stack Web Application</dd></div><div><dt>Domain</dt><dd>Fashion and Lifestyle E-commerce</dd></div><div><dt>Frontend</dt><dd>React</dd></div><div><dt>Backend</dt><dd>Node.js and Express</dd></div><div><dt>Database</dt><dd>MongoDB</dd></div></dl><ProjectLinks links={project.links} variant="modal" /></section>

    <Section title="Technology"><p>Kaushik’s Footprints is built using the MERN stack. React powers the customer storefront and admin interface, while Node.js and Express provide the backend API layer. MongoDB stores product details, user accounts and cart information.</p><p>The frontend communicates with the backend through REST APIs for product retrieval, authentication and cart operations. JWT tokens identify authenticated users when protected cart requests are made. The admin interface communicates with the same backend to upload images and manage the product catalogue.</p><div className="kf-tech-grid">{technologies.map(([name, detail]) => <article key={name}><h4>{name}</h4><p>{detail}</p></article>)}</div></Section>

    <Section title="Architecture / Workflow"><ProjectArchitecture architecture={project.caseStudy.architecture} /><ol className="kf-journey">{['The customer opens the React storefront.', 'The frontend requests product data from the Express backend.', 'The customer browses products by category.', 'The customer opens an individual product page.', 'The customer signs up or logs in.', 'The backend verifies the credentials and issues a JWT token.', 'The authenticated customer adds or removes cart items.', 'The backend updates that customer’s cart data in MongoDB.', 'The cart calculates item quantities and the total amount.', 'The customer can continue toward the checkout or order interface.', 'An administrator can upload images and manage catalogue products.', 'Updated product information becomes available to the storefront through the backend API.'].map((step, index) => <li key={step}><span>{index + 1}</span>{step}</li>)}</ol></Section>

    <Section title="Problem" tone="kf-problem"><p>Small fashion stores and emerging retail businesses often need an affordable way to present their catalogue online, manage product information and provide customers with a convenient shopping experience. Depending entirely on complex enterprise commerce platforms can be expensive or unnecessarily difficult for a smaller product catalogue.</p><p>The technical challenge was to create one connected application in which customers could discover products, maintain their own carts and authenticate their accounts, while administrators could manage the same product catalogue from a separate interface.</p><p>The platform therefore needed to solve several connected problems:</p><ul><li>Present fashion and lifestyle products in a clear and responsive storefront.</li><li>Organise products into customer-friendly categories.</li><li>Provide individual product pages containing pricing and product information.</li><li>Maintain cart data separately for every authenticated user.</li><li>Persist products, user records and carts beyond a single browser session.</li><li>Give administrators a convenient way to upload images and manage products.</li><li>Keep the storefront, backend, admin panel and database synchronised.</li></ul><strong className="kf-highlight">Design objective: Create a practical e-commerce foundation that connects customer shopping workflows with administrative product management through one backend and database.</strong></Section>

    <Section title="Solution" tone="kf-solution"><p>The solution was a multi-layered MERN e-commerce application consisting of a customer-facing React storefront, a separate React admin interface, an Express REST API and a MongoDB database.</p><p>The customer application retrieves dynamic product data from the backend and presents it through category pages, product-detail views and shopping-cart interfaces. Users can create an account, log in and perform user-specific cart operations through JWT-authenticated API requests.</p><p>The admin interface connects to the same backend and provides catalogue-management functionality. Administrators can upload product images, add new products, view the current catalogue and remove products. Because the storefront and admin interface share the same backend and database, catalogue changes can be reflected in the customer application.</p><div className="kf-feature-grid">{features.map(([name, detail]) => <article key={name}><h4>{name}</h4><p>{detail}</p></article>)}</div><aside className="kf-scope"><strong>Current scope:</strong> The verified implementation focuses on product browsing, authentication, persistent cart operations, product-image handling and admin catalogue management. The checkout interface represents the next stage of the customer journey. Do not claim that live payments or complete order persistence are available unless they have been implemented and verified.</aside></Section>

    <Section title="Challenges"><ol className="kf-challenge-grid">{challenges.map(([title, detail], index) => <li key={title}><span>{String(index + 1).padStart(2, '0')}</span><h4>{title}</h4><p>{detail}</p>{index === 7 && <em>Next-stage engineering</em>}</li>)}</ol></Section>

    <Section title="Lessons Learned"><div className="kf-lesson-grid">{lessons.map(([title, detail]) => <article key={title}><h4>{title}</h4><p>{detail}</p></article>)}</div><strong className="kf-highlight">Key takeaway: Kaushik’s Footprints strengthened my understanding of how customer experiences, backend services, authentication, database persistence and administrative workflows come together inside a practical full-stack application.</strong></Section>

    <Section title="Future Improvements" tone="kf-future"><p>These are future improvements, not currently implemented features.</p><ul className="kf-future-list">{future.map((item) => <li key={item}>{item}</li>)}</ul></Section>
    <div className="kf-footer-action"><ProjectLinks links={project.links} variant="modal" /></div>
  </div>
}

export default KaushikFootprintsCaseStudy
