import LegalLayout from "./LegalLayout";

export default function CompliancePage() {
  return (
    <LegalLayout title="Compliance" updatedAt="March 21, 2026">
      <h2 className="text-xl font-semibold text-slate-900">Regulatory Posture</h2>
      <p>
        Bimba3D operates with a privacy-first and contractual compliance approach, including customer terms, privacy policy, and data
        processing addendum.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">Data Governance</h2>
      <ul className="list-disc pl-6 space-y-2">
        <li>Retention controls by product policy and plan configuration.</li>
        <li>Project-level visibility controls (private/public) in the platform.</li>
        <li>Administrative access controls for operational oversight.</li>
      </ul>

      <h2 className="text-xl font-semibold text-slate-900">Subprocessors and Vendors</h2>
      <p>
        We use service providers for infrastructure and related operations under contractual protections and appropriate access boundaries.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">Export and Sanctions Compliance</h2>
      <p>
        Use of the platform is subject to applicable export controls, sanctions laws, and local regulations. Customers are responsible for
        lawful use and lawful data processing in their jurisdiction.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">Contact</h2>
      <p>
        For compliance documentation requests, contact sales@bimba3d.com or support@bimba3d.com.
      </p>
    </LegalLayout>
  );
}
