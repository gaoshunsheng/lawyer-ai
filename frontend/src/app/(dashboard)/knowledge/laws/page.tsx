import { LawSearch } from "@/components/knowledge/law-search";

export default function LawsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">法律法规</h1>
        <p className="text-muted-foreground mt-2">
          检索国家法律、行政法规、司法解释、地方性法规
        </p>
      </div>
      <LawSearch />
    </div>
  );
}
