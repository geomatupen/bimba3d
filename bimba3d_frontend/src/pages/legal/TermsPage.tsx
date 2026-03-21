import LegalLayout from "./LegalLayout";

export default function TermsPage() {
  return (
    <LegalLayout title="Terms of Service" updatedAt="March 21, 2026">
      <h2 className="text-xl font-semibold text-slate-900">1. Service Scope</h2>
      <p>
        Bimba3D provides cloud-hosted 3D reconstruction workflows for image processing, model generation, and related export/view
        features. Use of the platform is subject to account limits, platform policies, and applicable law.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">2. Accounts and Access</h2>
      <p>
        You are responsible for maintaining the confidentiality of your credentials and all activity under your account. You must
        provide accurate registration information and keep it updated.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">3. Customer Content</h2>
      <p>
        You retain rights to content you upload and outputs you generate, subject to third-party rights and applicable law. You grant
        Bimba3D limited rights to host, process, and transmit content solely to operate the service.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">4. Acceptable Use</h2>
      <p>
        You may not use the service for unlawful, abusive, or harmful purposes, including unauthorized access attempts, malware
        distribution, or processing data you are not authorized to use.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">5. Availability and Support</h2>
      <p>
        Service availability targets, support channels, and response times vary by plan and may change over time. Planned maintenance
        and emergency maintenance may temporarily affect availability.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">6. Billing and Subscription</h2>
      <p>
        Paid plans are billed according to your selected terms. Subscription, renewal, cancellation, and refund policies are governed by
        your plan and billing provider terms.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">7. Limitation of Liability</h2>
      <p>
        The service is provided on an “as is” and “as available” basis. To the extent permitted by law, Bimba3D disclaims implied
        warranties and limits liability for indirect, incidental, special, and consequential damages.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">8. Changes</h2>
      <p>
        We may update these terms periodically. Continued use of the service after updates constitutes acceptance of revised terms.
      </p>
    </LegalLayout>
  );
}
