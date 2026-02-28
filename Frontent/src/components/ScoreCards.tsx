const ScoreCards = () => {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Superpower Score Card */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-br from-[#8B4513] via-[#CD6839] to-[#F4A460] min-h-[280px]">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-black/40 to-transparent" />
        </div>
        <div className="relative z-10">
          <div className="mb-12">
            <p className="text-white/90 text-sm mb-2">superpower score</p>
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-bold text-white">70</span>
            </div>
            <p className="text-white/70 text-sm mt-1">on track</p>
          </div>
          
          <div className="mt-auto">
            <div className="relative h-2 bg-white/20 rounded-full">
              <div className="absolute h-2 bg-white rounded-full" style={{ width: '70%' }} />
            </div>
            <div className="flex justify-between text-white/60 text-xs mt-2">
              <span>0</span>
              <span>60</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Biological Age Card */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-br from-[#5F9B6B] to-[#7CB88E] min-h-[280px]">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-black/30 to-transparent" />
        </div>
        <div className="relative z-10">
          <div className="mb-12">
            <p className="text-white/90 text-sm mb-2">Biological age</p>
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-bold text-white">25</span>
            </div>
            <p className="text-white/90 text-xs font-medium mt-1">Age</p>
            <p className="text-white/70 text-sm">2.5 years younger</p>
          </div>
          
          <div className="mt-auto">
            <div className="relative h-2 bg-white/20 rounded-full">
              <div className="absolute h-2 bg-white rounded-full" style={{ width: '45%' }} />
            </div>
            <div className="flex justify-between text-white/60 text-xs mt-2">
              <span>0</span>
              <span>25</span>
              <span>65</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreCards;
