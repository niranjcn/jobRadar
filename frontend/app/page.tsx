import Link from "next/link";
import { RadarLoading } from "@/components/radar-loading";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-10 px-6">
      <div className="text-center">
        <div className="mb-6 flex justify-center">
          <RadarLoading label="" />
        </div>
        <div className="mb-3 font-mono text-xs uppercase tracking-[0.28em] text-primary">
          Edition 28 · Warm · Career intelligence
        </div>
        <h1 className="font-fraunces text-5xl font-extrabold tracking-[-0.02em]">JOBRADAR</h1>
        <p className="mx-auto mt-4 max-w-md text-[15px] leading-relaxed text-text-secondary">
          Find jobs before others.<br />
          JobRadar continuously monitors career pages and alerts you when the
          right opportunity appears.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link href="/browse" className="btn-primary">
            Browse Jobs
          </Link>
          <Link href="/dashboard" className="btn-ghost">
            Get Started
          </Link>
          <Link href="/sources" className="btn-ghost">
            View Sources
          </Link>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-3 font-mono text-xs tracking-widest text-text-muted">
        <span>WORKDAY</span>·<span>GREENHOUSE</span>·<span>LEVER</span>·
        <span>ASHBY</span>·<span>ORACLE</span>
      </div>
    </div>
  );
}