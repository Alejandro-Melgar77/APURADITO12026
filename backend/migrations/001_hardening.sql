-- Apply after the initial schema exists. All statements are idempotent so this
-- can safely be run in Supabase SQL Editor during an upgrade.
CREATE UNIQUE INDEX IF NOT EXISTS uq_conductores_usuario_id
    ON conductores (usuario_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_pagos_solicitud_viaje_id
    ON pagos (solicitud_viaje_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_consentimientos_usuario_politica
    ON consentimientos_usuario (usuario_id, politica_id);
