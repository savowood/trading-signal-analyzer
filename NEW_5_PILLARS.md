# NEW 5 PILLARS - Momentum Trading Scanner

**Trading Signal Analyzer v0.93**

---

## 🎯 Complete Overhaul of Stock Scanner

The momentum scanner has been completely redesigned with **NEW, more aggressive 5 Pillars** optimized for catching active momentum plays.

---

## 📊 NEW 5 PILLARS

### Pillar 1: Up 10%+ on the Day ⬆️
**Previous:** Any price movement
**Now:** Must be up at least 10% from today's open

**Why:**
- Filters for stocks already in motion
- Catches momentum early while it's building
- Eliminates choppy, directionless stocks
- Only shows UPWARD momentum (bullish bias)

**Impact:**
- You see stocks that are actively moving NOW
- No waiting for momentum to start
- Ready to enter on pullbacks

---

### Pillar 2: 500% Relative Volume (5x Average) 📊
**Previous:** 2x average volume
**Now:** 5x average volume (500% relative volume)

**Why:**
- Much stronger volume requirement
- Indicates significant institutional interest
- Filters out weak, low-conviction moves
- Volume confirms the price action

**Impact:**
- Only the most liquid, active stocks
- Better fills and tighter spreads
- Confirms genuine buying pressure
- Reduces false signals dramatically

---

### Pillar 3: News Event Moving Stock Higher 📰
**Previous:** Any catalyst (broad)
**Now:** Active news/catalyst detection with strength classification

**Detection Method:**
- Extreme intraday move (10%+) + explosive volume (5x)
- Strong weekly/monthly moves (bonus indicators)
- Classified as: STRONG | MODERATE | PRESENT

**Why:**
- There's a REASON for the move
- Fundamental driver behind technical setup
- Sustainable momentum (not just technical bounce)
- Attracts more buyers/attention

**Impact:**
- You know WHY the stock is moving
- More confidence in the trade
- Better risk/reward (catalyst-driven moves tend to extend)

---

### Pillar 4: Price Range $2-$20 (Configurable) 💵
**Previous:** $0.0001 - $20 (included sub-penny stocks)
**Now:** **DEFAULT: $2 - $20**

**Why This Range:**
- **$2 minimum:** Good liquidity, avoid most pump-and-dumps
- **$20 maximum:** Still affordable, good % move potential
- **Sweet spot:** Retail traders + institutions both active
- **Pattern Day Trading:** $2+ stocks more accessible

**Configurable Options:**
1. **Default ($2-$20)** - RECOMMENDED
2. **Penny stocks ($0.10-$2.00)** - Higher risk
3. **Sub-penny ($0.0001-$0.10)** - Extreme risk
4. **Mid-cap ($20-$100)** - Lower volatility
5. **Custom** - Your own range

**Why Configurable:**
- Different strategies for different traders
- Penny stock traders can still use the tool
- Advanced traders can scan any range
- Default keeps most users safe

---

### Pillar 5: Under 20M Shares Float 🎯
**Previous:** Under 100M shares float
**Now:** Under 20M shares float

**Why:**
- **Low float = Squeeze potential**
- Less shares = easier to move price
- Small orders create big % moves
- Gamma squeeze more likely (options)
- Short squeeze more explosive

**Impact:**
- Only the most squeezable stocks
- Maximum volatility potential
- Big % moves on moderate volume
- Runner potential

**Float Calculation:**
```
Float = Market Cap / Share Price / 1,000,000
```

If a stock has 15M float and shows up in scanner → 🌟 marked

---

## 🔥 What Changed From Previous Version

### Old Criteria (v0.92 and earlier):
1. 2x relative volume (loose)
2. Under 100M float (too broad)
3. $0.0001-$20 price (too many penny stocks)
4. Any catalyst (vague)
5. Pattern recognition (optional)

**Problem:** Too many results, too much noise, hard to find real plays

### New Criteria (v0.93):
1. **Up 10%+ TODAY** ✅
2. **5x relative volume** ✅
3. **News catalyst present** ✅
4. **$2-$20 (default)** ✅
5. **Under 20M float** ✅

**Result:** Fewer, higher-quality setups with genuine momentum

---

## 📈 Scanner Output Improvements

### New Display Format:
```
🔥 MOMENTUM SCANNER RESULTS - 5 PILLARS
═════════════════════════════════════════════════════════════════════════════

NEW 5 PILLARS: +10% Day | 5x RelVol | News Catalyst | $2-$20 | <20M Float
═════════════════════════════════════════════════════════════════════════════

#    Ticker   Price      Score   Today%     RelVol    Float(M)  
─────────────────────────────────────────────────────────────────────────────
1    XYZ      $5.67      5/5 🔥🔥🔥  +18.5%    12.3x     8.5⭐
2    ABC      $12.34     5/5 🔥🔥🔥  +15.2%    8.7x      15.2⭐
3    DEF      $8.90      4/5 🔥🔥    +12.1%    6.4x      25.3

⭐ = Low float (<20M shares)
💡 Sorted by: Score (pillars met) then Today's % change
```

**Key Improvements:**
- Shows today's % move prominently
- Low float indicator (⭐)
- Score out of 5 (must meet 3+ to appear)
- Sorted by best setups first
- Clear, actionable information

---

## 🎓 How to Use the New Scanner

### Step 1: Select Market
```
1. US Stocks (NASDAQ + NYSE) - RECOMMENDED
2. NASDAQ only
3. NYSE only
```

### Step 2: Choose Price Range
```
1. Default ($2.00 - $20.00) - RECOMMENDED
2. Penny stocks ($0.10 - $2.00)
3. Sub-penny ($0.0001 - $0.10)
4. Mid-cap ($20 - $100)
5. Custom range
```

**First time?** Use defaults (option 1 for both)

### Step 3: Review Results
Scanner shows stocks meeting 3+ of 5 pillars, sorted by:
1. How many pillars met (5/5 is best)
2. Today's % change (biggest movers first)

### Step 4: Select Stocks
Choose which stocks to analyze with VWAP/MACD for entry/exit points.

---

## 💡 Trading Strategy with New Pillars

### What You're Looking For:

**5/5 Pillars (Perfect Setup):**
- Stock up 15%+ today
- Volume 8x-10x+ average
- Clear news catalyst
- $5-$15 price range
- 10-15M float
- **Action:** Primary watchlist, highest probability

**4/5 Pillars (Strong Setup):**
- Stock up 10-12% today
- Volume 5x-7x average
- Likely catalyst (inferred from move)
- Good price/float
- **Action:** Secondary watchlist, good probability

**3/5 Pillars (Acceptable):**
- Meets minimum requirements
- One or two pillars missing
- **Action:** Watch carefully, need extra confirmation

### Entry Strategy:

1. **Scanner finds the stock** (meets 3-5 pillars)
2. **Analyze with VWAP/MACD** (get entry/exit points)
3. **Wait for pullback** to VWAP or key level
4. **Enter on bounce** with tight stop below support
5. **Target** next resistance or 3:1 R/R

### Risk Management:

- Stop loss below VWAP or institutional level
- Position size: 1-2% of account at risk
- Take profit: Scale out at resistance levels
- Never marry the position (momentum can reverse fast)

---

## ⚠️ Important Notes

### These Are Momentum Plays
- **Not long-term holds**
- Day trades or short-term swings
- High volatility = high risk
- Use proper position sizing

### Volume Matters
- 5x volume is AGGRESSIVE filter
- Some days scanner may find 0-5 stocks
- **That's OK!** Quality > Quantity
- Don't force trades on quiet days

### News/Catalyst
- Scanner detects statistical catalyst (move + volume)
- **You should still check actual news**
- Use: Benzinga, Twitter/X, company PR
- Confirm the "why" behind the move

### Low Float Can Mean High Risk
- More volatile (good and bad)
- Wider spreads possible
- Can reverse quickly
- Great for day trading, risky for holds

---

## 🆚 Comparison: Old vs New

| Aspect | Old (v0.92) | New (v0.93) |
|--------|-------------|-------------|
| **Min % Move** | Any | +10% today |
| **Rel Volume** | 2x | 5x (500%) |
| **Float** | <100M | <20M |
| **Price Default** | $0.0001-$20 | $2-$20 |
| **Catalyst** | Vague | Classified |
| **Results** | 20-50 stocks | 0-15 stocks |
| **Quality** | Mixed | High |
| **Focus** | Any setup | Active momentum |

---

## 🎯 Expected Results

### On Active Market Days:
- 5-15 stocks meeting criteria
- Multiple 5/5 pillar setups
- Clear momentum plays

### On Quiet Market Days:
- 0-5 stocks meeting criteria
- Fewer opportunities
- **Don't force trades!**

### Best Market Conditions:
- Market in uptrend
- High overall market volume
- News-driven volatility
- Sector rotation happening

---

## 🚀 Real-World Example

### Stock: XYZ (Hypothetical)

**Scanner Shows:**
```
Ticker: XYZ
Price: $8.50
Score: 5/5 🔥🔥🔥
Today: +18.5%
RelVol: 12.3x
Float: 8.5M ⭐
```

**What This Tells You:**
✅ **Pillar 1:** Up 18.5% (way above 10% minimum)
✅ **Pillar 2:** Volume 12.3x (crushing the 5x requirement)
✅ **Pillar 3:** Catalyst present (move this big = news)
✅ **Pillar 4:** $8.50 (perfect price range)
✅ **Pillar 5:** 8.5M float (very low, squeeze potential)

**Next Steps:**
1. Check news (what's the catalyst?)
2. Run VWAP/MACD analysis
3. Find entry point (pullback to VWAP?)
4. Set stop loss (below key level)
5. Define exit (take profit at resistance)

**Trade Example:**
- Entry: $8.60 (pullback to VWAP)
- Stop: $8.25 (below VWAP)
- Risk: $0.35 per share
- Target: $9.65 (3:1 R/R)
- Reward: $1.05 per share

---

## 💡 Pro Tips

### 1. **Use the Scanner Early in Trading Day**
Best results: 9:45 AM - 11:00 AM EST
- Morning momentum identified
- Volume confirming moves
- News digested by market

### 2. **Don't Chase**
- Stock up 18%? Don't buy at highs
- Wait for pullback to VWAP
- Let it prove support
- Then enter with tight stop

### 3. **Respect the Volume**
- 5x volume is THE confirmation
- No volume = no conviction
- Volume dries up? Exit

### 4. **News is King**
- Always check WHY stock is moving
- Bad news + momentum = potential reversal
- Good news + momentum = sustainable move
- No news + momentum = be cautious

### 5. **Scale Out**
- Take 1/3 at first resistance
- Take 1/3 at second resistance
- Let 1/3 run with trailing stop
- Lock in profits gradually

---

## 🎓 Educational Value

### What You'll Learn:
- How momentum stocks behave
- Volume/price relationship
- Catalyst-driven trading
- Float impact on volatility
- Risk management in fast moves

### Skills Developed:
- Quick decision making
- Entry/exit timing
- Reading momentum
- News interpretation
- Position sizing

---

## ⚖️ Risk Disclaimer

**These are aggressive momentum criteria designed for active trading.**

- High volatility = high risk
- Can lose money quickly
- Requires active monitoring
- Not suitable for beginners
- Paper trade first!

**Use proper risk management:**
- 1-2% account risk per trade
- Always use stop losses
- Don't trade more than you can afford to lose
- This is a TOOL, not financial advice

---

## 📊 Summary

**NEW 5 Pillars = Better Quality Momentum Plays**

✅ Fewer, higher-quality results
✅ Focus on active movers
✅ Built-in catalyst confirmation
✅ Optimized for day/swing trading
✅ Configurable for different strategies

**The Goal:**
Find stocks with genuine momentum, strong volume, a catalyst, good liquidity, and squeeze potential.

**The Result:**
Higher win rate, better setups, less noise.

---

**Ready to scan for momentum! 🔥**
