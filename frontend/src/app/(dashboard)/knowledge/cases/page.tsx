import { CaseSearch } from "@/components/knowledge/case-search";

export default function CasesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">判例文书</h1>
        <p className="text-muted-foreground mt-2">
          检索劳动争议、合同纠纷等典型案例和裁判文书
        </p>
      </div>
      <CaseSearch />
    </div>
  );
}
