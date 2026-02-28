import Navigation from "@/components/Navigation";
import ScoreCards from "@/components/ScoreCards";
import StatsCards from "@/components/StatsCards";
import BiomarkerList from "@/components/BiomarkerList";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="space-y-8">
          {/* Profile Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-foreground">Max Marchione</h2>
            <p className="text-sm text-muted-foreground">Last tested: Apr 28th, 2025</p>
          </div>

          <ScoreCards />
          <StatsCards />
          <BiomarkerList />
        </div>
      </main>
    </div>
  );
};

export default Index;
