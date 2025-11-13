# DATA VALIDATION

Validate Tapestry songs against Spotify API and enrich with metadata.

## 🚀 Quick Start

Process next 2,000 songs:
```bash
cd scripts
python run_full_validation.py --start-batch 9 --num-batches 4
python analyze_low_confidence.py
python prepare_tapestry_additions.py
python merge_to_tapestry.py
python analyze_tapestry.py
```

## 📊 Current Status

- **Validated**: 2,285 songs (6.8% of tapestry)
- **Batches Complete**: 1-8 (4,000 songs processed)
- **Validation Rate**: 54.4% high confidence
- **Next**: Batches 9-12 (songs 4000-6000)

## 📁 Structure

- `scripts/` - 8 core workflow scripts
- `batch_results/` - Validation outputs
- `youtube_check/` - 459 songs for YouTube fallback
- `MASTER_GUIDE.md` - Complete documentation
- `BATCHES_1-8_FINAL_REPORT.md` - Latest results

## 🎮 The Game

**"Let's Improve Our Valid Percents!"**

Current score: 54.4%  
Target: 70%+ (unlock Phase 2: audio features!)

---

*See MASTER_GUIDE.md for complete workflow details*
