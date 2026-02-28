interface Biomarker {
  name: string;
  category: string;
  status: "optimal" | "normal" | "out-range";
  value: string;
  chartData: number[];
}

const biomarkers: Biomarker[] = [
  { 
    name: "LDL Cholesterol", 
    category: "Heart health",
    status: "out-range", 
    value: "103 mg/dL",
    chartData: [85, 90, 88, 95, 103]
  },
  { 
    name: "Apolipoprotein B (ApoB)", 
    category: "Heart health",
    status: "optimal", 
    value: "42 mg/dL",
    chartData: [48, 45, 50, 46, 42]
  },
  { 
    name: "Vitamin D", 
    category: "Nutrienta",
    status: "normal", 
    value: "42.3ng/dL",
    chartData: [40, 41, 43, 42, 42.3]
  },
  { 
    name: "Ferritin", 
    category: "",
    status: "optimal", 
    value: "75ng dl",
    chartData: [70, 72, 75, 73, 75]
  },
];

const getStatusColor = (status: Biomarker["status"]) => {
  switch (status) {
    case "optimal":
      return "text-optimal";
    case "normal":
      return "text-normal";
    case "out-range":
      return "text-out-range";
  }
};

const getStatusLabel = (status: Biomarker["status"]) => {
  switch (status) {
    case "optimal":
      return "Optimal";
    case "normal":
      return "Normal";
    case "out-range":
      return "Out of Range";
  }
};

const getChartColor = (status: Biomarker["status"]) => {
  switch (status) {
    case "optimal":
      return "#10b981"; // emerald-500
    case "normal":
      return "#eab308"; // yellow-500
    case "out-range":
      return "#ec4899"; // pink-500
  }
};

const MiniSparkline = ({ data, color }: { data: number[]; color: string }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 80;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width="120" height="40" className="ml-auto" viewBox="0 0 100 100" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.2 }} />
          <stop offset="100%" style={{ stopColor: color, stopOpacity: 0.05 }} />
        </linearGradient>
      </defs>
      <polyline
        points={`0,100 ${points} 100,100`}
        fill={`url(#gradient-${color})`}
        stroke="none"
      />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="3"
        vectorEffect="non-scaling-stroke"
      />
      {data.map((value, index) => {
        const x = (index / (data.length - 1)) * 100;
        const y = 100 - ((value - min) / range) * 80;
        return (
          <circle
            key={index}
            cx={x}
            cy={y}
            r="4"
            fill={color}
            vectorEffect="non-scaling-stroke"
          />
        );
      })}
    </svg>
  );
};

const BiomarkerList = () => {
  return (
    <div className="bg-card rounded-3xl shadow-sm overflow-hidden">
      {biomarkers.map((biomarker, index) => (
        <div
          key={biomarker.name}
          className={`px-8 py-6 flex items-center gap-8 ${
            index !== biomarkers.length - 1 ? "border-b border-border" : ""
          }`}
        >
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-foreground mb-0.5">{biomarker.name}</h4>
            {biomarker.category && (
              <p className="text-sm text-muted-foreground">{biomarker.category}</p>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 ${getStatusColor(biomarker.status)}`}>
              <div className={`w-2 h-2 rounded-full bg-current`} />
              <span className="text-sm font-medium whitespace-nowrap">
                {getStatusLabel(biomarker.status)}
              </span>
            </div>
          </div>

          <span className="text-sm text-muted-foreground min-w-[90px] text-right">
            {biomarker.value}
          </span>

          <div className="w-32">
            <MiniSparkline data={biomarker.chartData} color={getChartColor(biomarker.status)} />
          </div>
        </div>
      ))}
    </div>
  );
};

export default BiomarkerList;
