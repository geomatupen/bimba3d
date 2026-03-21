import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CreateProject from "./pages/CreateProject";
import ProjectDetail from "./pages/ProjectDetail";
import Comparison from "./pages/Comparison";
import PublicResult from "./pages/PublicResult";
import TermsPage from "./pages/legal/TermsPage";
import PrivacyPage from "./pages/legal/PrivacyPage";
import DPAPage from "./pages/legal/DPAPage";
import SecurityPage from "./pages/legal/SecurityPage";
import CompliancePage from "./pages/legal/CompliancePage";
import ThirdPartyNoticesPage from "./pages/legal/ThirdPartyNoticesPage";
import { HMRStatusBanner } from "./HMRStatusBanner";

function App() {
  return (
    <>
      {import.meta.env.DEV && <HMRStatusBanner />}
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/create" element={<CreateProject />} />
        <Route path="/project/:id" element={<ProjectDetail />} />
        <Route path="/result/:id" element={<PublicResult />} />
        <Route path="/comparison/:id" element={<Comparison />} />
        <Route path="/legal/terms" element={<TermsPage />} />
        <Route path="/legal/privacy" element={<PrivacyPage />} />
        <Route path="/legal/dpa" element={<DPAPage />} />
        <Route path="/legal/security" element={<SecurityPage />} />
        <Route path="/legal/compliance" element={<CompliancePage />} />
        <Route path="/legal/third-party-notices" element={<ThirdPartyNoticesPage />} />
      </Routes>
    </>
  );
}

export default App;
