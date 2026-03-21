import LegalLayout from "./LegalLayout";

export default function PrivacyPage() {
  return (
    <LegalLayout title="Privacy Policy" updatedAt="March 21, 2026">
      <h2 className="text-xl font-semibold text-slate-900">1. Data We Collect</h2>
      <p>
        We collect account information (such as name and email), authentication/session records, uploaded project content, generated
        outputs, and limited operational telemetry required to run and secure the platform.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">2. How We Use Data</h2>
      <p>
        Data is used to authenticate users, process projects, provide requested features, maintain service reliability, detect abuse, and
        deliver support.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">3. Security Measures</h2>
      <p>
        We protect data in transit using TLS and apply access controls and environment-level safeguards designed to prevent unauthorized
        access.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">4. Retention</h2>
      <p>
        Retention periods depend on product configuration and plan terms. Data may be deleted automatically based on retention settings
        or on account request, subject to legal and operational constraints.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">5. Sharing and Processors</h2>
      <p>
        We do not sell customer data. We may share data with infrastructure and service providers that help deliver the platform (for
        example hosting, logging, email, and billing), under contractual controls.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">6. Your Rights</h2>
      <p>
        Depending on jurisdiction, you may request access, correction, deletion, or export of personal data. Contact support to submit a
        request.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">7. Contact</h2>
      <p>
        For privacy requests, contact support@bimba3d.com and include the email associated with your account.
      </p>
    </LegalLayout>
  );
}
