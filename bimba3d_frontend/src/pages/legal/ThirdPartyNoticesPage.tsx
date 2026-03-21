import LegalLayout from "./LegalLayout";

export default function ThirdPartyNoticesPage() {
  return (
    <LegalLayout title="Third-Party Notices" updatedAt="March 21, 2026">
      <p>
        Bimba3D uses third-party software components. The summary below reflects key runtime and processing components currently in use.
      </p>

      <h2 className="text-xl font-semibold text-slate-900">Core Components</h2>
      <ul className="list-disc pl-6 space-y-3">
        <li>
          <strong>COLMAP</strong> — New BSD (3-clause BSD style). Source and license: colmap/colmap repository (`COPYING.txt`).
        </li>
        <li>
          <strong>PyTorch</strong> — BSD-style license terms as published in pytorch/pytorch `LICENSE`.
        </li>
        <li>
          <strong>gsplat</strong> — Apache License 2.0 (nerfstudio-project/gsplat `LICENSE`).
        </li>
        <li>
          <strong>NVIDIA CUDA Toolkit</strong> — NVIDIA SDK EULA with CUDA Toolkit supplement and redistributable constraints as documented
          by NVIDIA.
        </li>
      </ul>

      <h2 className="text-xl font-semibold text-slate-900">Important Notes</h2>
      <ul className="list-disc pl-6 space-y-2">
        <li>Third-party licenses apply to those components and their respective dependencies.</li>
        <li>Use of NVIDIA components is subject to NVIDIA distribution and usage terms.</li>
        <li>Additional attribution requirements may apply for bundled or redistributed binaries.</li>
      </ul>

      <h2 className="text-xl font-semibold text-slate-900">Reference Links</h2>
      <ul className="list-disc pl-6 space-y-2 break-all">
        <li>COLMAP: https://github.com/colmap/colmap</li>
        <li>PyTorch: https://github.com/pytorch/pytorch</li>
        <li>gsplat: https://github.com/nerfstudio-project/gsplat</li>
        <li>CUDA EULA: https://docs.nvidia.com/cuda/eula/index.html</li>
      </ul>

      <p className="text-xs text-slate-500 pt-2">
        This page provides an operational summary and does not replace full license texts. For legal review, consult each upstream license
        document directly.
      </p>
    </LegalLayout>
  );
}
