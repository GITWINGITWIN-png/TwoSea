# Data quality and vertical land motion at Thai tide gauges (Ko Taphao Noi, Ko Lak, Fort Phrachula Chomklao), 1985–present

> Scope note: these notes cover Ko Taphao Noi (PSMSL 446 / UHSLC 148 / GLOSS 042), Ko Lak (PSMSL 174 / UHSLC 328 / GLOSS 039) and Fort Phrachula Chomklao (PSMSL 444). The project uses UHSLC **Research Quality (RQ)** hourly files `h148a.csv` and `h328a.csv` (see `scripts/fetch_data.py`, `data/MANIFEST.md`). "Documented" = written in a primary source cited inline. "Inference" = my reasoning, not verified by the data producers.
>
> **Main finding:** the UHSLC RQ quality document for Ko Taphao Noi says UHSLC **added +10 cm to all hourly data from the start of the series up to 31 March 2012**. UHSLC made this change after comparing the gauge with altimetry and with Langkawi and finding a step near 1 April 2012. PSMSL documents no matching correction. This alone largely explains the ~100 mm higher PSMSL−UHSLC level in 2015–2019. The 2006–2012 wander also has a documented cause: from 12 Oct 2005 to Jul 2013 UHSLC switched its primary channel to its own radar gauge.

## Q1. Post-seismic vertical land motion (VLM) in Thailand after the 2004 Mw 9.2 and 2005 Mw 8.6 earthquakes: size, time evolution, and effect on relative sea level (RSL) at Ko Taphao Noi and Ko Lak

### Takeaway
Before 2004, Phuket rose slowly at about +2.4 mm/yr. After the 2004 earthquake it switched to non-linear (exponentially decaying) subsidence of about 5–10 mm/yr in the first years. Total subsidence is about 10 cm by 2021. Over the same period the tide gauge shows RSL up by 12–16 cm, a smooth, multi-year signal with **no co-seismic vertical jump**. In the Gulf of Thailand (Ko Lak side), GPS shows post-seismic subsidence of about 4 mm/yr at Sattahip and Ko Sichang and about 13 mm/yr at Ko Mattaphon. Trisirisatayawong et al. (2011) left post-2004 tide-gauge data out of their trend analysis for that reason.

### Cited Findings
**Phuket / Ko Taphao Noi (Andaman coast)**
- Naeije, M.C., Simons, W.J.F., Pradit, S., Niemnil, S., Thongtham, N., Mustafar, M.A., Noppradit, P. (2022). "Monitoring Megathrust-Earthquake-Cycle-Induced Relative Sea-Level Changes near Phuket, South Thailand, Using (Space) Geodetic Techniques." *Remote Sensing* 14(20), 5145. doi:10.3390/rs14205145. Before 2004, RSL rise at Phuket was 1.0 ± 0.7 mm/yr, which is 2.4 ± 0.2 mm/yr below the absolute rise because of uplift. "After the earthquake, nonlinear post-seismic subsidence has caused the VLM to drop by 10 cm in the past 17 years, resulting, by the end of 2020, in a relative sea-level rise by up to 16 cm." — [Naeije et al. 2022, PDF](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf); [MDPI page](https://www.mdpi.com/2072-4292/14/20/5145/html)
- Same paper: altimetry (SALT) trend near KTN is 3.3 ± 0.4 mm/yr. SALT minus TG gives an apparent VLM of 2.3 ± 0.8 mm/yr, which "perfectly matches" the GNSS value of 2.4 ± 0.2 mm/yr before 2004. After 2004, RSL rose "by 16 cm, according to TG, and by 10 cm, according to GNSS"; over 17 years the GNSS VLM averages about 6 mm/yr — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Same paper, model details: after 2005 they replaced the linear trend with an exponential decay (time constant τ = 40 yr, half-life about 28 yr) for both TG RSL and GNSS VLM. Fitted amplitudes are TG −275 ± 4.0 cm and GNSS 131 ± 0.1 cm. TG residual RMS is 8.94 cm, against 6.22 cm for SALT. They used a 3σ outlier filter that removed the 1997 IOD low — [Naeije et al. 2022, Table 2–3](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Same paper: "In the vertical direction, no vertical co-seismic position jumps were detected at any of these earthquake epochs [2004 Mw 9.2, Mar 2005 Mw 8.6 Nias, Apr 2012 Mw 8.6/8.2]". Post-seismic subsidence "appears to be further diminishing as no significant (non-seasonal) height changes have been observed during the past 4 years" (2017–2021). KTPH 2017–2021 vertical velocity is −0.7 ± 0.5 mm/yr and PMBC is −0.8 ± 0.5 mm/yr — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Same paper: the TG fit and the SALT−GPS fit diverge more and more after 2004 ("similar but slightly growing deviation after"). The authors say "we do not have a direct explanation for this deviation", that "the tide gauge itself also did not manifest any clear jump", and that "Trying to align both RSL solutions by introducing a jump in the TG data and/or further tuning the models is part of ongoing investigation." — [Naeije et al. 2022, Sec. 4.2 and Fig. 7](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Same paper: the KTN gauge sits on a concrete platform on steel pillars on the seabed, about 4 km from PMBC (Cape Panwa). The co-located GNSS station KTPH was installed in August 2019 directly above the TG benchmark. The KTPH–PMBC baseline has vertical WRMS of 2.6 mm with no significant change over 2 years, plus a seasonal vertical signal of about 4 mm amplitude, attributed to thermal response of the platform — [Naeije et al. 2022, Sec. 3.3](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Simons, W.J.F. et al. (2019). "Vertical motion of Phuket Island (1994–2018) due to the Sumatra-Andaman mega-thrust earthquake cycle: impact on sea-level and consequences for coral reefs." *Marine Geology*. Phuket went "from stable quasi-linear uplift at 2.5 ± 0.2 mm/yr, to (temporary) non-linear subsidence rates of 5–10 mm/yr". RSL "slightly positive until the end of 2004, followed by a significant increase averaging ~9 mm/yr that accumulated in 12 ± 1 cm by the end of 2018" — [UHI Pure record](https://pure.uhi.ac.uk/en/publications/vertical-motion-of-phuket-island-19942018-due-to-the-sumatra-anda/)
- Niemnil, S., Simons, W., Naeije, M., Mustafar, A., Brown, B., Pradit, S. (2019), EGU2019-439 abstract: pre-quake uplift is given as "5 ± 1 mm/yr", with subsidence of 5–10 mm/yr "in the first 7 years". RSL increase averaged "about 10 mm/yr that accumulated in 7 ± 1 cm by the end of 2011". Phuket still moves horizontally "2 cm/yr slower in SW direction than the Sundaland platelet" — [EGU2019-439](https://meetingorganizer.copernicus.org/EGU2019/EGU2019-439.pdf). *Note the conflict:* this abstract's 5 ± 1 mm/yr pre-quake uplift disagrees with the 2.5 ± 0.2 mm/yr (Simons 2019) and 2.4 ± 0.2 mm/yr (Naeije 2022) in the peer-reviewed papers.
- Coseismic horizontal motion: Phuket moved about 25 cm ESE toward the rupture — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf). Satirapod et al. (2007a, as cited in Satirapod et al. 2010) reported coseismic horizontal displacements of about 33 cm in the south, 9 cm in the centre and about 3 cm in the north of Thailand — [Satirapod, Bamrungwong, Vigny, Lee (2010) "Change of Strain Rate in Thailand after the 26 December 2004 and 28 March 2005 Earthquakes Using GPS Measurements", *KSCE J. Civil Eng.* 14(2):215–220, doi:10.1007/s12205-010-0215-4](https://www.geologie.ens.fr/~vigny/articles/satirapod_etal_KSCE_2009.pdf)
- Other Andaman-coast gauges: Ranong shows about 22 cm of non-linear RSL increase from the end of 2004 to 2020, and an RSL fall of −2.9 ± 1.3 mm/yr before 2005, implying about 5.3 ± 1.4 mm/yr inter-seismic uplift. Most of the Marine Department (TMD) gauges (Ranong, Kantrang, Krabi, Tummarang) "have been relocated in the past 25 years and have a potentially high risk of benchmark height offsets." — [Naeije et al. 2022, Sec. 4.3](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)

**Gulf of Thailand (Ko Lak side)**
- Trisirisatayawong, I., Naeije, M., Simons, W., Fenoglio-Marc, L. (2011). "Sea level change in the Gulf of Thailand from GPS-corrected tide gauge data and multi-satellite altimetry." *Global and Planetary Change* 76: 137–151. GPS-corrected absolute trends: Sattahip (1942–2004) 5.0 ± 1.3 mm/yr, Ko Sichang (1940–1999) 4.5 ± 1.3 mm/yr, Ko Mattaphon (1964–2004) 4.4 ± 1.1 mm/yr. **Ko Lak** altimetry trend for 1993–2009 is 3.6 ± 0.7 mm/yr. Using altimetry−TG VLM (Topex track collocated with the gauge), the Ko Lak 1940–2004 absolute rate is 3.0 ± 1.5 mm/yr. "Post-2004 tidal data have been treated separately in our study because reliable values of region-wide vertical co-seismic displacements and postseismic velocities caused by the 2004 Mw9.2 Sumatra-Andaman earthquake are still not accurately known." — [abstract via TCCN](https://tccnclimate.com/เอกสารงานวิจัย/เอกสารตีพิมพ์/item/147-sea-level-change-in-the-gulf-of-thailand-from-gps-corrected-tide-gauge-data-and-multi-satellite-altimetry)
- Same paper (as summarised in search snippets): the 2004 earthquake caused a transition from uplift to subsidence, with post-seismic downward motion of −3.9 mm/yr at Sattahip and Ko Sichang and −12.7 mm/yr at Ko Mattaphon — [search summary of Trisirisatayawong et al. 2011](https://tccnclimate.com/เอกสารงานวิจัย/เอกสารตีพิมพ์/item/147-sea-level-change-in-the-gulf-of-thailand-from-gps-corrected-tide-gauge-data-and-multi-satellite-altimetry) (number taken from the search snippet; not checked against the full text)
- After the quake, horizontal motion over all of Thailand turned SW (post-seismic relaxation on the Sumatran trench). The Nias Mw 8.6–8.7 earthquake of 28 March 2005 complicated the RTSD GPS campaigns — [Satirapod et al. 2010](https://www.geologie.ens.fr/~vigny/articles/satirapod_etal_KSCE_2009.pdf)

### Inferences
- At Ko Taphao Noi, the post-seismic VLM is a **smooth, slowly decaying ramp** (about 6 mm/yr on average, larger early on). It is not a step. In annual or monthly series it adds a trend change and low-frequency curvature from 2005 onward. It **cannot** make two datasets from the *same* gauge disagree with each other, because PSMSL and UHSLC both measure RSL at the same gauge, so VLM cancels in PSMSL−UHSLC. **Our PSMSL−UHSLC discrepancy must therefore come from instrument, datum or processing differences (see Q2), not from land motion.** VLM does matter for the *content* of each series (an RSL trend change after 2005 that a wavelet analysis will see as low-frequency power).
- Naeije et al. find TG RSL up 16 cm against 10 cm from GNSS after 2004, and they used HDRTN hourly data with only the PSMSL +14 mm 1988 correction. That 6 cm excess is the same order as the 10 cm reference shift UHSLC found near April 2012 (Q2). This hints, without proving it, that the HDRTN/PSMSL lineage still contains an uncorrected datum offset after 2005.
- Ko Lak (Gulf of Thailand, about 11.8°N) is far from the trench. Post-seismic subsidence there is probably a few mm/yr, by analogy with Sattahip and Ko Sichang (−3.9 mm/yr), but no Ko Lak-specific GNSS rate was found.

### Gaps
- No published GNSS vertical time series *at Ko Lak* was found. The Ko Lak post-2004 VLM is inferred from neighbouring Gulf stations only.
- Full-text Trisirisatayawong et al. (2011) figures (post-seismic VLM at each station) were not accessed. The −3.9 and −12.7 mm/yr values come from a search-engine summary.
- Panumastrakul et al. was not found in this session (the search did not surface it), so its numbers are not included.
- Simons et al. (2019) volume and page numbers were not verified.

## Q2. PSMSL and UHSLC documentation for these stations, and why PSMSL and UHSLC differ at Ko Taphao Noi after 2005

### Takeaway
The two archives hold **different instrument lineages and different datum corrections** after 2005.
- **Instruments:** from 12 Oct 2005 to 25 Jul 2013 UHSLC used its own radar gauge on the platform. UHSLC then took Royal Thai Navy (RTN) radar data from the Panwa Cape temporary site, 4 km away (to Feb 2016), and from 1 Mar 2016 the RTN radar on the rebuilt platform. PSMSL's data authority is the RTN Hydrographic Department.
- **Datum:** UHSLC **added +10 cm to all data before 1 April 2012** after an altimetry comparison. It also warns that the reference level is unstable at times and says to "use this series with caution". PSMSL documents only the 1988 +14 mm datum raise and the 1987 and 1998 benchmark changes.
- **Gaps:** the 2013–2014 PSMSL gap matches the destruction of the platform in July 2013.

### Cited Findings
**PSMSL station 446 (Ko Taphao Noi)**
- Data authority is the Oceanographic Division, Hydrographic Department, Royal Thai Navy, Bangkok. RLR 1940–2024, 94% complete. Documentation (2011-07-12): "From 1987 onwards the benchmark was BM 105 5.429m above the 1940-1987 datum. In 1988 the datum was raised 14mm. BM 105 then became 5.415m above the revised 1988 datum. In 1998 the primary benchmark became AS-1/2531 5.304m relative to the 1988 datum." RLR(1981) is 9.8 m below BM S.I. (1991). The page has **no note** about the 2004 tsunami, the 2005 instrument change, the 2012 shift, or the 2013 platform loss — [PSMSL 446](https://psmsl.org/data/obtaining/stations/446.php)
- The PSMSL RLR monthly file for 446 has **no values for any month of 2004, 2013 or 2014**. The 2005–2012 and 2015–2020 months are present with the "flag for attention" = 0. A few months have missing-day counts of 1–2 (e.g. 2011-01, 2015-07, 2016-01) — [PSMSL 446 RLR monthly file](https://psmsl.org/data/obtaining/rlr.monthly.data/446.rlrdata) (read directly on 2026-10-07)
- Naeije et al. note that the PSMSL rule accepts months with ≥15 days, while they required ≥2/3 of hourly values. They applied "+14 mm" from 1988 onward "as documented by PSMSL" to HDRTN hourly data — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)

**UHSLC JASL Research Quality station 148A (Ko Taphao Noi)** — all items from [UHSLC QA document qa148a.dmt, updated 16 Jun 2020](https://uhslc.soest.hawaii.edu/rqds/indian/doc/qa148a.dmt)
- Contributors: the Naval Hydrographic Dept., RTN, and, "for 12 Oct 2005 - Jul 2013 in collaboration with RTN", UHSLC itself.
- Instruments: (1) RTN mechanical float gauge (STD), historic. (2) UHSLC radar (Vega Vegapuls 62) from 12 Oct 2005. (3) UHSLC pressure transducer from 12 Oct 2005. (4) Handar encoder from 20 Mar 2013. (5) RTN radar at Panwa Cape, 1 Nov 2012 – 28 Feb 2016. (6) RTN radar at Ko Taphao Noi from 1 Mar 2016.
- **Primary channel used in JASL 148A:** "1985-11 Oct 2005: STD (RTN); 12 Oct 2005 - 25 Jul 2013: UHSLC RAD; 26 Jul 2013 - 28 Feb 2016: RTN RAD Panwa Cape; 01 Mar 2016 - : RTN RAD TN". Short gaps in UHSLC RAD were filled with other channels. Missing UHSLC data were filled with RTN data for 24 Dec 2009 – 3 Jan 2010.
- Datum statement, verbatim: "The 10-day means from altimeter data are a useful comparison for long-term reference level stability. The comparison suggested a step-function shift near April 1, 2012. There is also a shift seen in the comparison of daily means with Langkawi. **Thus, historic hourly data from the beginning of the series to March 31, 2012 had 10 cm added.**"
- Also verbatim: "Given the reference level uncertainties described above, use this series with caution."
- Earlier adjustment: "+10 cm from 12Z 18 Nov - 23Z 31 Dec 1987" (uncertainty a few cm), based on residual analysis and comparison with West Malaysian stations.
- Undocumented level jumps that UHSLC flagged against Langkawi and in hourly residuals, which RTN "could not identify" as gauge errors:
  - 19 Jul–1 Aug 1989: −12 cm
  - 1 Nov 1990 – 1 Jul 1991: −7 cm
  - 1 Dec 1993 – 19 Mar 1994: +10 cm
  - 19 Mar–17 May 1994: −7 cm
  - 30 Nov 1996 – 20 Jan 1997: +15 cm
  
  UHSLC adds: "These signatures could very well be natural."
- 2004 tsunami: "A tsunami caused the large fluctuations on 26 Dec, 2004." The 2004 row shows 99% completeness, with only days 363–364 missing.
- Platform history: "The RTN and UHSLC tide gauges were located on a platform 80 m off the shore. The platform was destroyed by a storm in July 2013. The platform was subsequently rebuilt in 2016." Panwa Cape (7°48′05″N, 98°24′23″E, about 4 km away) radar data were "leveled to the TN datum". Tidal phases are the same at both sites, but amplitudes differ slightly.
- All series (UHSLC, Panwa Cape, new TN platform) are "linked to the historic RTN reference zero for TN". This reference zero "is not an official datum".
- Processing: hourly = spot hourly (RTN) or a 3-point Hanning filter (others). Daily = 119-point Bloomfield convolution filter. Monthly = mean of daily values, "calculated if 7 or fewer days are missing". RQ span is 1985-01-01 to 2019-12-31. Gaps longer than one month: Oct 2001, Jul 2002, Jul–Aug 2003, Jan–Feb 2004.
- Many repeated hourly "replaced or bad data" blocks appear in late 2012 and in May–July 2013 (days 151–205), just before the platform was lost.

**Conflict on the dates of platform loss and restoration**
- Naeije et al. (2022): the KTN TG "was destroyed after being hit by a fishing boat during a storm in the summer of 2013". A temporary TG at the PMBC jetty ran from 2012 to 2016. KTN was "recommissioned in January 2015". The 2013–2014 data are "unavailable in the GLOSS/PSMSL database" — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- This conflicts with UHSLC, which says the rebuilt platform was operational from 1 Mar 2016 and the Panwa Cape data were used through Feb 2016 — [UHSLC qa148a](https://uhslc.soest.hawaii.edu/rqds/indian/doc/qa148a.dmt)

**Ko Lak (PSMSL 174; UHSLC 328A)**
- PSMSL: authority RTN Hydrographic Dept. RLR 1940–2024, 97% complete. RLR(1981) is 8.4 m below BM A. In 2009 PSMSL noted that the 2008 data from RTN had "erroneous" missing-days information (e.g. 720.95 days). RTN insisted it was correct, and PSMSL took the missing-days data from the JASL CD instead — [PSMSL 174](https://psmsl.org/data/obtaining/stations/174.php)
- UHSLC 328A: analog mechanical float gauge with hourly digitisation, RTN contributor, 1985–2019. A box-car jump on 4–7 Sep 1996 was corrected by subtracting 550 cm. "The daily and monthly means reveal no apparent changes in the reference level." Residuals show fluctuations above 30 cm with 1–3 day periods. There are low-completeness years: 2004 (80%), 2005 (82%; gap 24 Mar – 1 May 2005), 2006 (83%) — [UHSLC qa328a](https://uhslc.soest.hawaii.edu/rqds/pacific/doc/qa328a.dmt)

**Fort Phrachula Chomklao (PSMSL 444)**
- PSMSL notes:
  - "There is what appears to be a datum shift from 2003 onwards... the Authority has said that the offset for the data is 0.583m" (2008).
  - "2005 data flagged suspect. Data looks way out - authority contacted to confirm datum etc." (2006).
  - Benchmark change from 1987: from BM PJ2, 4.41 m above gauge datum, to BM 1, 5.826 m above datum.
  - "Sharp increase of trend after data gap in early 1960s".
  - For submergence, PSMSL points to Emery & Aubrey (1991).
  
  Source: [PSMSL 444](https://psmsl.org/data/obtaining/stations/444.php)

### Inferences
- **Quantitative check (my own calculation, not published).** I compared PSMSL 446 RLR monthly values with monthly means of the project's UHSLC RQ hourly file `h148a.csv` (months with ≥20 days of hourly data). I removed the 1990–2003 mean offset (4828 mm) and computed annual means of PSMSL−UHSLC (mm):
  - 1990–2003: within ±3 mm (1985 +10, 1986 −13)
  - 2005: −5
  - 2006: +17; 2007: +37; 2008: +9; 2009: +72; 2010: −27; 2011: +112; 2012: +79
  - 2015: +117; 2016: +102; 2017: +101; 2018: +127; 2019: +126
  
  This reproduces the discrepancy described in the brief.
- **About +100 mm after 2015:** this is the expected signature of UHSLC's documented +10 cm addition to all data before April 2012, *if* PSMSL/RTN made no matching correction. Aligning on 1990–2003, a period where UHSLC carries the +100 mm, puts UHSLC 2015–2019 about 100 mm *below* PSMSL. This is the most likely explanation and is directly documented on the UHSLC side. Both archives' post-2016 data come from the same RTN radar, so the residual 2015–2019 spread (101–127 mm) probably reflects monthly-mean processing differences and/or small additional datum handling differences (unverified).
- **2006–2012 wander (±70 mm):** after 12 Oct 2005 UHSLC used its *own* radar gauge, while PSMSL's RTN-supplied values presumably come from the RTN float gauge (STD) on the same platform. **Two different instruments with independent reference-level errors** explains why agreement breaks exactly at 2005. That PSMSL uses the RTN STD gauge for 2005–2012 is plausible but not stated by PSMSL.
- The PSMSL−UHSLC monthly difference does **not** step cleanly at 1 April 2012. It is already about +100 to +115 through mid-2011 to March 2012, falls to about +55 to +60 for May–Oct 2012, and is +31 in Nov 2012. This suggests the RTN/PSMSL series has its own reference shifts in 2009–2012, independent of UHSLC's April 2012 step. Which series is "right" in those years cannot be decided without altimetry or Langkawi comparisons.
- UHSLC filled late 2012 and mid-2013 with many short gaps and switched to Panwa Cape data from 26 Jul 2013. The PSMSL 2013–2014 gap is consistent with the platform loss in July 2013 and RTN not submitting the Panwa Cape temporary-site data to PSMSL. That last point is inference: PSMSL does not explain the gap.
- PSMSL RLR also lacks *all* of 2004, while UHSLC has 2004 at 99% completeness. Any PSMSL-based analysis therefore has gaps in both 2004 and 2013–2014.
- **Practical recommendation (inference):**
  - (a) Do not splice or average PSMSL and UHSLC for Ko Taphao Noi after 2005.
  - (b) Pick one archive and treat 2005-10-12, 2012-04-01, 2013-07-26 and 2016-03-01 as candidate break dates.
  - (c) Run sensitivity analyses: (i) pre-2005 only, (ii) the full UHSLC RQ series as distributed, (iii) UHSLC with the +100 mm adjustment removed.
  - (d) Check with an independent reference (altimetry SLA near 7.83°N, 98.42°E, or Langkawi, PSMSL/UHSLC).

### Gaps
- PSMSL's processing notes for 446 after 2005 are missing. It is unclear which RTN instrument PSMSL's 2005–2012 and 2015+ data come from, and whether RTN applied any offset. No documentation was found.
- No RTN Hydrographic Department (hydro.navy.mi.th) metadata or levelling history was accessed.
- UHSLC Fast Delivery (FD) metadata for 148 was not retrieved. It is unknown whether FD carries the +10 cm pre-2012 adjustment. The project uses RQ, so this matters less.
- The SONEL GNSS@TG page for KTPH (Ko Taphao Noi) was not checked.
- PSMSL "Ko Taphao Noi" may be revised in future when RTN supplies 2013–2014 or corrected data. The current page says "Extracted from Database 28 Sep 2026; last update 04 Aug 2025".

## Q3. Known problems combining Thai tide-gauge records; subsidence at Bangkok and Fort Phrachula from groundwater pumping

### Takeaway
Thai gauges are run by two agencies, RTN Hydrographic Department and the Marine Department. Many gauges have been relocated, are founded on piles or sediment, or have undocumented benchmark offsets. The Chao Phraya mouth gauges (Fort Phrachula / Pom Phrachun, Bangkok Bar) carry large subsidence signals and are routinely left out of regional sea-level studies. Bangkok subsidence peaked at about 10–12 cm/yr around 1978–1981 and fell to about 2–3 cm/yr (InSAR, locally) and ≤5 mm/yr (deep GNSS) after pumping controls. The Fort Phrachula PSMSL record also has a documented 0.583 m datum offset from 2003 and a suspect 2005 year.

### Cited Findings
- Thailand's long gauges were "established in 1940 as part of a network of tide gauges operated by the Royal Thai Navy (RTN) and the Thai Marine Department (TMD)". TMD gauges in south Thailand (Ranong, Kantrang, Krabi, Tummarang) were mostly relocated within the past 25 years and carry "a potentially high risk of benchmark height offsets" — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Vossepoel, F., Soonthornrangsan, J., Lazecky, M., Hooper, A., Niemnil, S., Simons, W.J.F., Naeije, M., Slangen, A., Aobpaet, A. (2024). "Integration of Satellite Subsidence and Sea-Level Data for Evaluating the Mean High-Water Line in the Bangkok Region: Preliminary Result." GIS-IDEAS 2024, IEEE, doi:10.1109/GIS-IDEAS63212.2024.10990512 — [TU Delft repository PDF](https://repository.tudelft.nl/file/File_d5243779-d71f-416f-bc30-3418c930293b). Findings:
  - Pom Phrachunlachomklao and Bangkok Bar "do not have a foundation on the bedrock, and trend lines of the position of these gauges strongly suggest an influence of the settling of the sand layers on which the supporting piles stand". For this reason they "were excluded from the earlier sea-level analysis of the Gulf of Thailand" (Trisirisatayawong et al. 2011).
  - The tide gauge near Bangkok shows RSL rise "up to 15 mm per year over the past 60 years".
  - InSAR (2015–2022) shows subsidence of "up to 3 cm/yr". Deep GNSS (BNKK, RTSD, CUSV, SPKN) shows "absolute subsidence rates (below 20 m) up to 5 mm/yr in the past 25 years".
  - Modelled (ESMDA) annual subsidence for 1980–2012 is "between 0-10 cm/yr which is almost linear since 1990 due to ban for ground water pumping".
  - Bangkok is "currently sinking at a rate of 2-3 cm/yr".
  - RTSD has run annual levelling since 1978.
  - Station SPKN had a ~1 cm position shift in March 2019 after its pier was hit (a reminder that monuments get disturbed).
- JpGU 2013 abstracts: Bangkok "is subsiding with a rate of 20 mm/year in recent years" after groundwater-pumping limits from the late 1980s. In 1981 "the highest subsidence rate up to 120 mm/year had been recorded in the eastern area". ALOS/PALSAR PSInSAR (Nov 2007 – Dec 2010) shows about 1 cm/yr *uplift* near central Bangkok, correlated with groundwater recovery — [JpGU 2013 STT57-02](https://www2.jpgu.org/meeting/2013/session/PDF/S-TT57/STT57-02_E.pdf) (conference abstracts; lower evidential weight)
- Fort Phrachula PSMSL datum issues (datum shift from 2003, 0.583 m offset per the Authority; 2005 suspect; benchmark change 1987; trend jump after the early-1960s gap) — [PSMSL 444](https://psmsl.org/data/obtaining/stations/444.php)
- Trisirisatayawong et al. (2011) handled the earthquake by dropping post-2004 tide data from long-term trends. They handled VLM with GPS campaign corrections, or altimetry−TG differencing at Ko Lak — [abstract](https://tccnclimate.com/เอกสารงานวิจัย/เอกสารตีพิมพ์/item/147-sea-level-change-in-the-gulf-of-thailand-from-gps-corrected-tide-gauge-data-and-multi-satellite-altimetry)
- Region-wide context: SE Asian land-height change is dominated by groundwater-driven subsidence (Manila, Bangkok) and by post-seismic subsidence in Thailand, Peninsular Malaysia and Singapore after the Sumatran earthquakes since 2004, "lasting for years or even decades" — [Otago/NTU summary as returned by search](https://www.otago.ac.nz/__data/assets/pdf_file/0023/332825/understanding-tectonic-vertical-land-motions-for-relative-sea-level-changes-in-southeast-asia-through-geodetic-observations-and-earthquake-models-0243187.pdf) (PDF could not be parsed; claim taken from the search snippet only)

### Inferences
- Fort Phrachula should not be used for climate-index coherence without explicit detrending or segmenting. A 0.583 m datum offset from 2003, a suspect 2005, and multi-cm/yr subsidence make it dominated by land and datum effects. If it is used at all, analyse only periods inside one datum epoch, after a high-pass filter.
- Ko Lak looks like the cleanest of the three in UHSLC RQ: "no apparent changes in the reference level" after the 1996 box-car fix. Its 2004–2006 completeness is low (80–83%), so monthly means in those years carry more gap noise.

### Gaps
- No peer-reviewed rate specific to the Fort Phrachula gauge site was found. Vossepoel et al. give a Bangkok-area tide-gauge figure (≤15 mm/yr RSL over 60 yr) without naming the station explicitly in the text I read.
- Phien-wej et al. (2006) and Aobpaet et al. (2013) InSAR were cited by others but not accessed directly.
- The news-sourced "10 cm/yr in the late 1970s" figure (World Bank/ADB/JBIC study via Inquirer) was not used as a primary fact.

## Q4. How datum and benchmark errors propagate into interannual (wavelet/coherence) analyses; methods for tide-gauge homogenisation

### Takeaway
The standard practice for detecting reference-level offsets is to compare the tide gauge with altimetry, or with a neighbouring gauge. It can detect offsets of 1–2 cm at good sites, and UHSLC uses it routinely, which is how the Ko Taphao Noi April 2012 step was found. Offsets are usually identified by eye or semi-subjectively and then estimated by least squares with an AR(1) error model. I found no Thailand-specific literature on how such steps bias wavelet coherence, so the propagation analysis below is inference.

### Cited Findings
- Ray, R.D., Widlansky, M.J., Genz, A.S., Thompson, P.R. (2023). "Offsets in tide-gauge reference levels detected by satellite altimetry: ten case studies." *Journal of Geodesy* 97(12):110. doi:10.1007/s00190-023-01800-7. Findings:
  - "Offsets as small as 1–2 cm can be detected when both altimeter and tide gauge successfully observe the same ocean signal."
  - Detection is best at small open-ocean islands and harder near large land masses, because coastal altimetry is weaker there.
  - Offsets were identified subjectively and then estimated by least squares, with standard errors allowing AR(1) serial correlation.
  - Reference-level offsets "most commonly occur because of reinstallation of sensors".
  - The method "is explicitly called for in the quality-control manuals of the Intergovernmental Oceanographic Commission" (UNESCO/IOC 2020) and is "routinely used at the University of Hawai'i Sea Level Center".
  - No Thai stations are among the ten cases.
  
  Sources: [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10694126); [Springer](https://link.springer.com/article/10.1007/s00190-023-01800-7)
- At Ko Taphao Noi, UHSLC compared 10-day altimetry means and daily means at Langkawi (Malaysia) to find and correct the April 2012 step (+10 cm before) and the 1987 adjustment. It used Langkawi comparisons to flag 1989–1997 jumps of 7–15 cm that it did not correct — [UHSLC qa148a](https://uhslc.soest.hawaii.edu/rqds/indian/doc/qa148a.dmt)
- Naeije et al. (2022) advocate SALT, TG and GNSS "combined in pairs to validate each independent result (e.g., SALT − GNSS = TG)", and note the combination "allow[s] the validation of existing tide gauges (and detection of potential height offsets)". For KTN they model post-2004 RSL with an exponential decay (τ = 40 yr) rather than step terms, and use a 3σ outlier filter — [Naeije et al. 2022](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-05145/article_deploy/remotesensing-14-05145.pdf)
- Altimetry–tide-gauge comparison is also used operationally by AVISO/CNES Cal/Val, through annual in-situ tide-gauge reports and OSTST presentations such as "Possible datum errors at tide gauges detected by satellite altimetry: some case studies" (OSTST 2022) — [OSTST 2022 presentation](https://ostst.aviso.altimetry.fr/fileadmin/user_upload/OSTST2022/Presentations/CVL2022-Possible_datum_errors_at_tide_gauges_detected_by_satellite_altimetry__some_case_studies.pdf); [AVISO TG report 2015](https://www.aviso.altimetry.fr/fileadmin/documents/calval/annual_report_insitu_TG_2015_02.pdf) (not opened; listed as pointers)

### Inferences
- **Propagation to wavelet and coherence (inference, not from a cited paper).**
  - A step of size Δ at time t₀ in a monthly series behaves like a Heaviside function, whose spectrum falls off as 1/f. It adds power across all scales, mostly at long periods, and it is localised around t₀ in the continuous wavelet transform: a vertical "flame" at t₀ that widens with scale.
  - A 100 mm step is large next to Ko Taphao Noi's interannual sea-level variability (UHSLC flagged natural-looking 7–15 cm jumps). It can therefore create spurious 2–8 yr power and phase-locked structure near 2012–2015, and distort wavelet coherence with ENSO/IOD indices there.
  - The 2013–2014 gap adds edge and cone-of-influence effects at the same time.
  - A multi-year ramp, such as post-seismic VLM, biases mainly the longest periods (and the trend). It affects the 2–7 yr ENSO/IOD band less after detrending or high-pass filtering.
- **Sensible checks for the project (inference):**
  - (i) Difference the station against an independent reference (altimetry SLA at the gauge, or Langkawi) and look for steps at the documented dates: 2005-10-12, 2012-04-01, 2013-07-26, 2016-03-01.
  - (ii) Estimate offsets by least squares with AR(1) errors, following Ray et al. 2023. Alternatively use a formal change-point test, such as a penalised likelihood or PELT-type method. This is a common general technique, but I found no Thai application.
  - (iii) Repeat the wavelet coherence on (a) pre-2005, (b) the full series with the documented UHSLC adjustments, and (c) the series with steps removed. Treat coherence near the break dates as unreliable.

### Gaps
- No peer-reviewed study was found that quantifies how tide-gauge datum steps bias wavelet coherence with climate indices. The propagation argument is reasoning only.
- No published homogenised Ko Taphao Noi or Ko Lak series was found, nor any change-point study of Thai tide gauges.
- The OSTST and AVISO documents were not opened, so it is unknown whether they mention Ko Taphao Noi or Ko Lak.
