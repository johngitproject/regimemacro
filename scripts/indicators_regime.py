# Indicateurs de régime — stdlib uniquement (ADX Wilder / ADXR / Hurst DFA).
# Usage perso. Aucune dépendance (pas de pandas/numpy).
# Refs : Wilder 1978 (ADX), Kaufman 1995 (ER, non inclus ici), DFA Peng et al. 1994.
import math


def wilder_adx(highs, lows, closes, period=14):
    """ADX Wilder exact. Entrées : listes alignées H/L/C.
    Retour : dict {adx, plus_di, minus_di} listes alignées (None en warmup).
    Convention Wilder : premier ATR/DM = somme des `period` premiers TR/DM,
    puis lissage ATR = ATRprev - ATRprev/n + TR. Premier ADX = moyenne des
    `period` premiers DX, puis ADX = (ADXprev*(n-1)+DX)/n.
    """
    n = len(closes)
    adx = [None] * n
    pdi = [None] * n
    mdi = [None] * n
    if n < 2 * period + 1:
        return {"adx": adx, "plus_di": pdi, "minus_di": mdi}
    trs, pdms, mdms = [], [], []
    for i in range(1, n):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        ph, pl = highs[i - 1], lows[i - 1]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        up = h - ph
        dn = pl - l
        pdm = up if (up > dn and up > 0) else 0.0
        mdm = dn if (dn > up and dn > 0) else 0.0
        trs.append(tr)
        pdms.append(pdm)
        mdms.append(mdm)
    # trs[0] correspond à la barre 1 (index 1 de closes)
    atr = sum(trs[:period])
    pdm_s = sum(pdms[:period])
    mdm_s = sum(mdms[:period])
    dxs = []  # (index_close, dx)
    for k in range(period, len(trs) + 1):
        if k > period:
            # lissage avec le TR/DM courant (trs[k-1] = barre k)
            atr = atr - atr / period + trs[k - 1]
            pdm_s = pdm_s - pdm_s / period + pdms[k - 1]
            mdm_s = mdm_s - mdm_s / period + mdms[k - 1]
        if atr == 0:
            dx = 0.0
            pd, md = 0.0, 0.0
        else:
            pd = 100.0 * pdm_s / atr
            md = 100.0 * mdm_s / atr
            denom = pd + md
            dx = 100.0 * abs(pd - md) / denom if denom != 0 else 0.0
        idx = k  # index dans closes (trs[k-1] <-> closes[k])
        if idx < n:
            pdi[idx] = pd
            mdi[idx] = md
            dxs.append((idx, dx))
    # Premier ADX = moyenne des `period` premiers DX
    if len(dxs) < period:
        return {"adx": adx, "plus_di": pdi, "minus_di": mdi}
    first_avg = sum(d for _, d in dxs[:period]) / period
    last_idx = dxs[period - 1][0]
    adx[last_idx] = first_avg
    prev = first_avg
    for idx, dx in dxs[period:]:
        prev = (prev * (period - 1) + dx) / period
        adx[idx] = prev
    return {"adx": adx, "plus_di": pdi, "minus_di": mdi}


def adxr_from_adx(adx, period=14):
    """ADXR[i] = (ADX[i] + ADX[i-period]) / 2. None si indisponible."""
    out = [None] * len(adx)
    for i, v in enumerate(adx):
        if v is None or i - period < 0 or adx[i - period] is None:
            continue
        out[i] = (v + adx[i - period]) / 2.0
    return out


def _linfit_slope_intercept(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    return a, my - a * mx


def dfa_alpha(returns, scales=None):
    """Exposant DFA-1 sur une série de rendements (log ou simples).
    Retour None si insuffisant. alpha ~0.5 = bruit, >0.55 = persistant,
    <0.45 = anti-persistant. Stdlib.
    """
    x = [v for v in returns if v is not None]
    n = len(x)
    if n < 64:
        return None
    mean = sum(x) / n
    y = []
    acc = 0.0
    for v in x:
        acc += v - mean
        y.append(acc)
    if scales is None:
        scales = [16, 24, 32, 48, 64, 96, 128]
    lns, lfs = [], []
    for s in scales:
        if s < 8 or s > n // 4:
            continue
        k = n // s
        if k < 2:
            continue
        f2_sum = 0.0
        cnt = 0
        for b in range(k):
            seg = y[b * s:(b + 1) * s]
            xs = list(range(s))
            a, bb = _linfit_slope_intercept(xs, seg)
            var = sum((yy - (a * xx + bb)) ** 2 for xx, yy in zip(xs, seg)) / s
            f2_sum += var
            cnt += 1
        if cnt == 0 or f2_sum <= 0:
            continue
        f = math.sqrt(f2_sum / cnt)
        if f <= 0:
            continue
        lns.append(math.log(s))
        lfs.append(math.log(f))
    if len(lns) < 2:
        return None
    slope, _ = _linfit_slope_intercept(lns, lfs)
    return slope
