import LegalLayout from "./LegalLayout";

export default function SecurityPage() {
  return (
    <LegalLayout title="Security" updatedAt="March 21, 2026">
      <h2 className="text-xl font-semibold text-slate-900">Security Principles</h2>
      <p>
        Bimba3D applies layered controls across network, application, and operational boundaries to protect customer data and service
        integrity.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">Data Protection</h2>
      <ul className="list-disc pl-6 space-y-2">
        <li>Encryption in transit using TLS.</li>
        <li>Access-limited infrastructure and authenticated API access.</li>
        <li>Role-aware authorization for project visibility and management.</li>
      </ul>

      <h2 className="text-xl font-semibold text-slate-900">Operational Security</h2>
      <ul className="list-disc pl-6 space-y-2">
        <li>Service health checks and operational logging.</li>
        <li>Controlled deployment and dependency management practices.</li>
        <li>Incident response workflow with issue triage and remediation.</li>
      </ul>

      <h2 className="text-xl font-semibold text-slate-900">Responsible Disclosure</h2>
      <p>
        If you identify a security issue, please report it privately to support@bimba3d.com with steps to reproduce, impact summary, and
        contact details for coordinated disclosure.
      </p>
    </LegalLayout>
  );
}
