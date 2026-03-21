import LegalLayout from "./LegalLayout";

export default function DPAPage() {
  return (
    <LegalLayout title="Data Processing Addendum (DPA)" updatedAt="March 21, 2026">
      <h2 className="text-xl font-semibold text-slate-900">1. Roles</h2>
      <p>
        For customer project data, customer acts as Data Controller and Bimba3D acts as Data Processor, processing data only on
        documented instructions and to provide contracted services.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">2. Processing Scope</h2>
      <p>
        Processing includes storage, transformation, model training/inference workflows, export generation, and service telemetry strictly
        necessary for platform operation and support.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">3. Security Controls</h2>
      <p>
        Bimba3D applies technical and organizational controls appropriate to the risk profile, including encrypted transport, access
        management, and service monitoring.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">4. Subprocessors</h2>
      <p>
        Bimba3D may use vetted subprocessors for hosting, storage, communications, and billing. A current list is maintained in the
        compliance materials and provided upon request.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">5. International Transfers</h2>
      <p>
        Where required, cross-border transfers are handled through lawful transfer mechanisms and contractual safeguards.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">6. Data Subject Requests</h2>
      <p>
        Bimba3D provides reasonable assistance for customer responses to data subject rights requests where legally required.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">7. Deletion and Return</h2>
      <p>
        At contract end or request, customer data is deleted or returned according to service capabilities, legal obligations, and retention
        controls.
      </p>
    </LegalLayout>
  );
}
