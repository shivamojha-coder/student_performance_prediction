import { BookOpen, ChevronDown, EyeOff, KeyRound, Lightbulb, Upload } from "lucide-react";

const navLinks = ["Dashboard", "Goal Setting", "My Results"];

function GlassCard({ title, icon: Icon, children }) {
  return (
    <article className="glass-card">
      <header className="card-head">
        <h3 className="card-title">{title}</h3>
        <div className="glass-icon" aria-hidden="true">
          <Icon size={18} />
        </div>
      </header>
      {children}
    </article>
  );
}

function Field({ label, type = "text", placeholder, value, icon }) {
  return (
    <label className="field-group">
      <span className="field-label">{label}</span>
      <div className="field-control">
        <input className="glass-input" type={type} placeholder={placeholder} defaultValue={value} />
        {icon ? <span className="field-icon">{icon}</span> : null}
      </div>
    </label>
  );
}

function SelectField({ label, value, options = [] }) {
  return (
    <label className="field-group">
      <span className="field-label">{label}</span>
      <div className="field-control">
        <select className="glass-input glass-select" defaultValue={value}>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <span className="field-icon" aria-hidden="true">
          <ChevronDown size={16} />
        </span>
      </div>
    </label>
  );
}

function Toggle({ label, defaultChecked }) {
  return (
    <div className="toggle-row">
      <span className="toggle-label">{label}</span>
      <label className="toggle">
        <input type="checkbox" defaultChecked={defaultChecked} />
        <span className="toggle-track">
          <span className="toggle-thumb" />
        </span>
      </label>
    </div>
  );
}

export default function App() {
  return (
    <div className="settings-shell">
      <div className="ambient-orb orb-one" />
      <div className="ambient-orb orb-two" />
      <div className="ambient-orb orb-three" />

      <nav className="glass-nav">
        <div className="nav-inner">
          <div className="brand-block">
            <div className="brand-mark">PH</div>
            <span className="brand-text">PredictorHub</span>
          </div>

          <div className="nav-links">
            {navLinks.map((item) => (
              <button key={item} className={`nav-link ${item === "My Results" ? "active" : ""}`} type="button">
                {item}
              </button>
            ))}
          </div>

          <button className="profile-pill" type="button">
            <span className="profile-avatar">S</span>
            <span className="profile-meta">
              <span className="profile-name">Shivam Ojha</span>
              <span className="profile-id">STU-6507-19</span>
            </span>
          </button>
        </div>
      </nav>

      <main className="settings-main">
        <header className="page-head">
          <p className="page-kicker">Manage account preferences</p>
          <h1 className="page-title">Account Settings</h1>
        </header>

        <section className="settings-grid">
          <GlassCard title="Personal Information" icon={BookOpen}>
            <div className="field-stack">
              <Field label="Full Name" value="Shivam Ojha" />
              <Field label="Email" type="email" value="shivam.ojha@example.com" />

              <div className="profile-upload-row">
                <div className="profile-image-wrap">
                  <img
                    className="profile-image"
                    src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=facearea&w=128&h=128&q=80"
                    alt="Profile"
                  />
                </div>

                <button className="upload-tile" type="button">
                  <span className="upload-title">
                    <Upload size={15} />
                    Upload picture
                  </span>
                  <span className="upload-subtitle">PNG or JPG up to 5MB</span>
                </button>
              </div>
            </div>
          </GlassCard>

          <GlassCard title="Academic Preferences" icon={Lightbulb}>
            <div className="field-stack">
              <SelectField
                label="Current Class"
                value="Computer Science 101"
                options={["Computer Science 101", "Data Science 201", "Product Design 102"]}
              />

              <SelectField label="Section" value="Section A" options={["Section A", "Section B", "Section C"]} />

              <Field label="Target Study Hours" type="number" value="35" />

              <div className="toggle-stack">
                <Toggle label="Email Notifications" defaultChecked />
                <Toggle label="Push Notifications" defaultChecked />
              </div>
            </div>
          </GlassCard>

          <GlassCard title="Security" icon={KeyRound}>
            <div className="field-stack">
              <Field label="Current Password" type="password" placeholder="Enter current password" />
              <Field
                label="New Password"
                type="password"
                placeholder="Enter new password"
                icon={<EyeOff size={15} />}
              />
              <Toggle label="Two-Factor Authentication" />
            </div>
          </GlassCard>
        </section>

        <section className="action-row">
          <button className="primary-button" type="button">
            Save Changes
          </button>
        </section>
      </main>
    </div>
  );
}
