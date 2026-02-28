const StatsCards = () => {
  const total = 106;
  const optimal = 80;
  const inRange = 21;
  const outOfRange = 5;

  const optimalPercent = (optimal / total) * 100;
  const inRangePercent = (inRange / total) * 100;
  const outOfRangePercent = (outOfRange / total) * 100;

  return (
    <div className="bg-card rounded-3xl p-8 shadow-sm">
      <h3 className="text-sm text-muted-foreground mb-6">Biomarkers</h3>
      
      <div className="grid grid-cols-4 gap-8 mb-6">
        <div>
          <div className="text-5xl font-bold text-foreground mb-1">106</div>
          <div className="text-sm text-muted-foreground">Total</div>
        </div>
        <div>
          <div className="text-5xl font-bold text-muted-foreground/40 mb-1">80</div>
          <div className="text-sm text-muted-foreground">Optimal</div>
        </div>
        <div>
          <div className="text-5xl font-bold text-muted-foreground/40 mb-1">21</div>
          <div className="text-sm text-muted-foreground">In range</div>
        </div>
        <div>
          <div className="text-5xl font-bold text-muted-foreground/40 mb-1">5</div>
          <div className="text-sm text-muted-foreground">Out of range</div>
        </div>
      </div>

      {/* Stacked Bar Chart */}
      <div className="relative h-2 bg-muted rounded-full overflow-hidden flex">
        <div 
          className="bg-optimal h-full" 
          style={{ width: `${optimalPercent}%` }}
        />
        <div 
          className="bg-at-range h-full" 
          style={{ width: `${inRangePercent}%` }}
        />
        <div 
          className="bg-out-range h-full" 
          style={{ width: `${outOfRangePercent}%` }}
        />
      </div>
    </div>
  );
};

export default StatsCards;
