import os, collections
exec(open(os.path.expanduser('~/scripts/indx_build.py')).read().split('# ---------- resolver self-test')[0])
A, _ = parse_user(RP + 'filament/Prusament PLA Galaxy Red @COREONE.ini')
B, _ = parse_user(RP + 'filament/Prusament PLA Galaxy Red @COREONEINDX HF0.4.ini')
Pc = resolve('filament', 'Prusament PLA @COREONE'); Pi = resolve('filament', 'Prusament PLA @COREONEINDX HF0.4')
IG = {'filament_settings_id'}
def s(v, n=46): v = v.replace('\\n', ' / '); return v if len(v) <= n else v[:n] + '...'
print('A = "Prusament PLA Galaxy Red @COREONE"  (yours, inherits Prusament PLA @COREONE): %d keys' % len(A))
print('B = "Prusament PLA Galaxy Red @COREONEINDX HF0.4" (imported, inherits: "%s"): %d keys\n' % (B.get('inherits', ''), len(B)))
print('--- A vs B: values that differ (key | yours | imported)')
for k in sorted(set(A) & set(B)):
    if k in IG or k in ('inherits', 'compatible_printers_condition'): continue
    if not eq(A[k], B[k]): print('  %-34s | %-30s | %s' % (k, s(A[k], 30), s(B[k], 30)))
print('\n--- keys only in A (imported preset lacks them -> PrusaSlicer fills defaults):', sorted(set(A) - set(B)))
print('--- keys only in B:', sorted(set(B) - set(A)))
print('\n--- B vs the official INDX parent "Prusament PLA @COREONEINDX HF0.4": INDX tuning the imported preset does NOT carry')
miss = [k for k in Pi if k not in B and k in A and k not in IG]
print('  parent defines these, imported preset has no value (default used):', sorted(miss))
print('  parent value differs from imported value:')
for k in sorted(B):
    if k in Pi and k not in IG and k not in ('inherits', 'compatible_printers_condition') and not eq(B[k], Pi[k]):
        print('    %-34s | imported %-24s | INDX parent %s' % (k, s(B[k], 24), s(Pi[k], 30)))
print('\n--- A vs its parent "Prusament PLA @COREONE": your own tweaks')
for k in A:
    if k in IG or k in ('inherits',): continue
    if k in Pc and not eq(A[k], Pc[k]): print('    %-34s | yours %-24s | parent %s' % (k, s(A[k], 24), s(Pc[k], 30)))
print('\n--- Open PrintTag record: temp 205-225 (mid 215), bed 40-60 (mid 50), density 1.24, colour #8d2129')
for k in ('temperature', 'first_layer_temperature', 'bed_temperature', 'first_layer_bed_temperature', 'filament_density', 'filament_colour', 'filament_notes', 'filament_vendor', 'filament_cost', 'filament_spool_weight', 'filament_type', 'start_filament_gcode'):
    print('    %-30s yours=%-22s imported=%-22s INDX parent=%s' % (k, s(A.get(k, '-'), 22), s(B.get(k, '-'), 22), s(Pi.get(k, '-'), 24)))
