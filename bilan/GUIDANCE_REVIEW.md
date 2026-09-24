# Validation humaine — codage forward guidance FOMC (33 meetings)

Protocole : pour chaque ligne, lire le corps complet (`donnees/regime/sources/fomc_statements/YYYYMMDD_body.txt`), vérifier que la citation existe et que la stance draft correspond au ton du statement, puis cocher. En cas de desaccord : barrer le draft et ecrire la stance retenue + motif.
Une fois les 33 lignes traitees : statut -> `valide_aaaa-mm-jj`, re-signer SHA256SUMS.

## 01. 2022-01-26 14:00 — decision +0bp (hold)
- Stance draft : **neutral** (score 0) — `action[hold]+0`
- Citation : _In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook. The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of the Committee's goals._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220126a.htm — corps : `donnees/regime/sources/fomc_statements/20220126_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 02. 2022-03-16 14:00 — decision +25bp (hike)
- Stance draft : **hawkish** (score 4) — `H[ongoing increases]+2; action[hike]+2`
- Citation : _With appropriate firming in the stance of monetary policy, the Committee expects inflation to return to its 2 percent objective and the labor market to remain strong. In support of these goals, the Committee decided to raise the target range for the federal funds rate to 1/4 to 1/2 percent and anticipates that ongoing increases in the target range will be appropriate._
- Dissents : Voting against this action was James Bullard, who preferred at this meeting to raise the target range for the federal funds rate by 0.5 percentage point to 1/2 to 3/4 percent. Patrick Harker voted as an alternate member at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220316a.htm — corps : `donnees/regime/sources/fomc_statements/20220316_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 03. 2022-05-04 14:00 — decision +50bp (hike)
- Stance draft : **hawkish** (score 5) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. With appropriate firming in the stance of monetary policy, the Committee expects inflation to return to its 2 percent objective and the labor market to remain strong._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220504a.htm — corps : `donnees/regime/sources/fomc_statements/20220504_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 04. 2022-06-15 14:00 — decision +75bp (hike)
- Stance draft : **hawkish** (score 5) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. In support of these goals, the Committee decided to raise the target range for the federal funds rate to 1-1/2 to 1-3/4 percent and anticipates that ongoing increases in the target range will be appropriate._
- Dissents : Voting against this action was Esther L. George, who preferred at this meeting to raise the target range for the federal funds rate by 0.5 percentage point to 1-1/4 percent to 1-1/2 percent. Patrick Harker voted as an alternate member at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220615a.htm — corps : `donnees/regime/sources/fomc_statements/20220615_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 05. 2022-07-27 14:00 — decision +75bp (hike)
- Stance draft : **hawkish** (score 5) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. In support of these goals, the Committee decided to raise the target range for the federal funds rate to 2-1/4 to 2-1/2 percent and anticipates that ongoing increases in the target range will be appropriate._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220727a.htm — corps : `donnees/regime/sources/fomc_statements/20220727_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 06. 2022-09-21 14:00 — decision +75bp (hike)
- Stance draft : **hawkish** (score 5) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. In support of these goals, the Committee decided to raise the target range for the federal funds rate to 3 to 3-1/4 percent and anticipates that ongoing increases in the target range will be appropriate._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20220921a.htm — corps : `donnees/regime/sources/fomc_statements/20220921_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 07. 2022-11-02 14:00 — decision +75bp (hike)
- Stance draft : **hawkish** (score 7) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. The Committee anticipates that ongoing increases in the target range will be appropriate in order to attain a stance of monetary policy that is sufficiently restrictive to return inflation to 2 percent over time._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20221102a.htm — corps : `donnees/regime/sources/fomc_statements/20221102_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 08. 2022-12-14 14:00 — decision +50bp (hike)
- Stance draft : **hawkish** (score 7) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. The Committee anticipates that ongoing increases in the target range will be appropriate in order to attain a stance of monetary policy that is sufficiently restrictive to return inflation to 2 percent over time._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20221214a.htm — corps : `donnees/regime/sources/fomc_statements/20221214_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 09. 2023-02-01 14:00 — decision +25bp (hike)
- Stance draft : **hawkish** (score 7) — `H[ongoing increases]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee is highly attentive to inflation risks. The Committee anticipates that ongoing increases in the target range will be appropriate in order to attain a stance of monetary policy that is sufficiently restrictive to return inflation to 2 percent over time._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm — corps : `donnees/regime/sources/fomc_statements/20230201_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 10. 2023-03-22 14:00 — decision +25bp (hike)
- Stance draft : **hawkish** (score 7) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee remains highly attentive to inflation risks. The Committee anticipates that some additional policy firming may be appropriate in order to attain a stance of monetary policy that is sufficiently restrictive to return inflation to 2 percent over time._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230322a.htm — corps : `donnees/regime/sources/fomc_statements/20230322_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 11. 2023-05-03 14:00 — decision +25bp (hike)
- Stance draft : **hawkish** (score 7) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent to which additional policy firming may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230503a.htm — corps : `donnees/regime/sources/fomc_statements/20230503_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 12. 2023-06-14 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hold]+0`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230614a.htm — corps : `donnees/regime/sources/fomc_statements/20230614_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 13. 2023-07-26 14:00 — decision +25bp (hike)
- Stance draft : **hawkish** (score 7) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hike]+2`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230726a.htm — corps : `donnees/regime/sources/fomc_statements/20230726_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 14. 2023-09-20 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hold]+0`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20230920a.htm — corps : `donnees/regime/sources/fomc_statements/20230920_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 15. 2023-11-01 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hold]+0`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20231101a.htm — corps : `donnees/regime/sources/fomc_statements/20231101_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 16. 2023-12-13 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[additional policy firming]+2; H[highly attentive to inflation risks]+1; H[cumulative tightening]+1; H[lags with which monetary policy]+1; action[hold]+0`
- Citation : _The Committee remains highly attentive to inflation risks. In determining the extent of any additional policy firming that may be appropriate to return inflation to 2 percent over time, the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy affects economic activity and inflation, and economic and financial developments._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20231213a.htm — corps : `donnees/regime/sources/fomc_statements/20231213_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 17. 2024-01-31 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[highly attentive to inflation risks]+1; D[reduce the target range]+2; D[gained greater confidence]+2; action[hold]+0`
- Citation : _The economic outlook is uncertain, and the Committee remains highly attentive to inflation risks. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm — corps : `donnees/regime/sources/fomc_statements/20240131_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 18. 2024-03-20 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[highly attentive to inflation risks]+1; D[reduce the target range]+2; D[gained greater confidence]+2; action[hold]+0`
- Citation : _The economic outlook is uncertain, and the Committee remains highly attentive to inflation risks. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240320a.htm — corps : `donnees/regime/sources/fomc_statements/20240320_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 19. 2024-05-01 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 6) — `H[highly attentive to inflation risks]+1; D[reduce the target range]+2; D[gained greater confidence]+2; D[slow the pace]+1; action[hold]+0`
- Citation : _The economic outlook is uncertain, and the Committee remains highly attentive to inflation risks. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240501a.htm — corps : `donnees/regime/sources/fomc_statements/20240501_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 20. 2024-06-12 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 5) — `H[highly attentive to inflation risks]+1; D[reduce the target range]+2; D[gained greater confidence]+2; action[hold]+0`
- Citation : _The economic outlook is uncertain, and the Committee remains highly attentive to inflation risks. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240612a.htm — corps : `donnees/regime/sources/fomc_statements/20240612_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 21. 2024-07-31 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 4) — `D[reduce the target range]+2; D[gained greater confidence]+2; action[hold]+0`
- Citation : _The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240731a.htm — corps : `donnees/regime/sources/fomc_statements/20240731_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 22. 2024-09-18 14:00 — decision -50bp (cut)
- Stance draft : **neutral** (score 1) — `D[gained greater confidence]+2; D[roughly in balance]+1; action[cut]-2`
- Citation : _The Committee has gained greater confidence that inflation is moving sustainably toward 2 percent, and judges that the risks to achieving its employment and inflation goals are roughly in balance. In considering additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks._
- Dissents : Voting against this action was Michelle W. Bowman, who preferred to lower the target range for the federal funds rate by 1/4 percentage point at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm — corps : `donnees/regime/sources/fomc_statements/20240918_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 23. 2024-11-07 14:00 — decision -25bp (cut)
- Stance draft : **neutral** (score -1) — `D[roughly in balance]+1; action[cut]-2`
- Citation : _In considering additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20241107a.htm — corps : `donnees/regime/sources/fomc_statements/20241107_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 24. 2024-12-18 14:00 — decision -25bp (cut)
- Stance draft : **neutral** (score 0) — `D[extent and timing of additional adjustments]+1; D[roughly in balance]+1; action[cut]-2`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against the action was Beth M. Hammack, who preferred to maintain the target range for the federal funds rate at 4-1/2 to 4-3/4 percent.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm — corps : `donnees/regime/sources/fomc_statements/20241218_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 25. 2025-01-29 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 2) — `D[extent and timing of additional adjustments]+1; D[roughly in balance]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250129a.htm — corps : `donnees/regime/sources/fomc_statements/20250129_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 26. 2025-03-19 14:00 — decision +0bp (hold)
- Stance draft : **hawkish** (score 2) — `D[extent and timing of additional adjustments]+1; D[slow the pace]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. Beginning in April, the Committee will slow the pace of decline of its securities holdings by reducing the monthly redemption cap on Treasury securities from $25 billion to $5 billion._
- Dissents : Voting against this action was Christopher J. Waller, who supported no change for the federal funds target range but preferred to continue the current pace of decline in securities holdings.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250319a.htm — corps : `donnees/regime/sources/fomc_statements/20250319_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 27. 2025-05-07 14:00 — decision +0bp (hold)
- Stance draft : **neutral** (score 1) — `D[extent and timing of additional adjustments]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250507a.htm — corps : `donnees/regime/sources/fomc_statements/20250507_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 28. 2025-06-18 14:00 — decision +0bp (hold)
- Stance draft : **neutral** (score 1) — `D[extent and timing of additional adjustments]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : unanime
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250618a.htm — corps : `donnees/regime/sources/fomc_statements/20250618_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 29. 2025-07-30 14:00 — decision +0bp (hold)
- Stance draft : **neutral** (score 1) — `D[extent and timing of additional adjustments]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against this action were Michelle W. Bowman and Christopher J. Waller, who preferred to lower the target range for the federal funds rate by 1/4 percentage point at this meeting. Absent and not voting was Adriana D. Kugler.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250730a.htm — corps : `donnees/regime/sources/fomc_statements/20250730_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 30. 2025-09-17 14:00 — decision -25bp (cut)
- Stance draft : **dovish** (score -2) — `action[cut]-2`
- Citation : _In considering additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against this action was Stephen I. Miran, who preferred to lower the target range for the federal funds rate by 1/2 percentage point at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20250917a.htm — corps : `donnees/regime/sources/fomc_statements/20250917_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 31. 2025-10-29 14:00 — decision -25bp (cut)
- Stance draft : **dovish** (score -2) — `action[cut]-2`
- Citation : _In considering additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against this action were Stephen I. Miran, who preferred to lower the target range for the federal funds rate by 1/2 percentage point at this meeting, and Jeffrey R. Schmid, who preferred no change to the target range for the federal funds rate at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm — corps : `donnees/regime/sources/fomc_statements/20251029_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 32. 2025-12-10 14:00 — decision -25bp (cut)
- Stance draft : **neutral** (score -1) — `D[extent and timing of additional adjustments]+1; action[cut]-2`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against this action were Stephen I. Miran, who preferred to lower the target range for the federal funds rate by 1/2 percentage point at this meeting; and Austan D. Goolsbee and Jeffrey R. Schmid, who preferred no change to the target range for the federal funds rate at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20251210a.htm — corps : `donnees/regime/sources/fomc_statements/20251210_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________

## 33. 2026-01-28 14:00 — decision +0bp (hold)
- Stance draft : **neutral** (score 1) — `D[extent and timing of additional adjustments]+1; action[hold]+0`
- Citation : _In considering the extent and timing of additional adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. In assessing the appropriate stance of monetary policy, the Committee will continue to monitor the implications of incoming information for the economic outlook._
- Dissents : Voting against this action were Stephen I. Miran and Christopher J. Waller, who preferred to lower the target range for the federal funds rate by 1/4 percentage point at this meeting.
- Source : https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm — corps : `donnees/regime/sources/fomc_statements/20260128_body.txt`
- Statut actuel : `draft_a_valider`
- [ ] Stance validee telle quelle
- [ ] Corrigee -> nouvelle stance : __________  Motif : __________
