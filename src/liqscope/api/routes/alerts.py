"""Rutas de la API para gestión y envío de alertas de liquidación a Telegram."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from liqscope.config import Settings
from liqscope.connectors.telegram import TelegramClient

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_settings() -> Settings:
    """Proveedor de dependencias para la configuración."""
    return Settings()


class TelegramTestRequest(BaseModel):
    """Solicitud de prueba de conectividad con Telegram."""

    bot_token: str | None = Field(default=None, description="Token del bot (opcional si está en .env)")
    chat_id: str | None = Field(default=None, description="Chat ID de destino (opcional si está en .env)")


class TelegramSendAlertRequest(BaseModel):
    """Solicitud de despacho de una alerta de liquidación a Telegram."""

    bot_token: str | None = Field(default=None, description="Token del bot (opcional si está en .env)")
    chat_id: str | None = Field(default=None, description="Chat ID de destino (opcional si está en .env)")
    title: str = Field(description="Título de la alerta")
    symbol: str = Field(default="BTCUSDT", description="Par analizado (BTCUSDT, ETHUSDT)")
    price: float = Field(gt=0, description="Precio de liquidación del clúster")
    delta_pct: float = Field(description="Distancia porcentual al Mark Price")
    volume_usd: float = Field(default=0.0, ge=0, description="Volumen estimado en USD")
    leverage: str = Field(default="50x", description="Apalancamiento dominante")
    side: str = Field(default="SHORT", description="Lado de las posiciones (LONG o SHORT)")
    tactical_tip: str = Field(default="", description="Recomendación o acción táctica sugerida")


class TelegramResponse(BaseModel):
    """Respuesta estándar del servicio de alertas."""

    success: bool = Field(description="Indica si la operación en Telegram fue exitosa")
    message: str = Field(description="Mensaje de estado o detalle del error")


@router.get(
    "/telegram/status",
    summary="Estado de configuración de Telegram",
    description="Consulta si el servicio de Telegram cuenta con credenciales activas sin exponer tokens.",
)
async def get_telegram_status(settings: Settings = Depends(get_settings)) -> dict[str, bool]:
    """Retorna el estado de disponibilidad del canal de Telegram."""
    has_token = bool(settings.telegram_bot_token.strip())
    has_chat = bool(settings.telegram_chat_id.strip())
    return {
        "configured": has_token and has_chat,
        "has_token": has_token,
        "has_chat": has_chat,
        "alerts_enabled": settings.telegram_alerts_enabled,
    }


@router.post(
    "/telegram/detect-chat",
    summary="Detectar Chat ID automáticamente",
    description="Consulta getUpdates para detectar el chat_id del último usuario que envió un mensaje o pulsó /start en el bot.",
)
async def detect_telegram_chat(
    payload: TelegramTestRequest,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Detecta automáticamente el chat_id a partir de los mensajes recientes."""
    token = (payload.bot_token or settings.telegram_bot_token).strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere Bot Token para consultar actualizaciones.",
        )

    client = TelegramClient(bot_token=token, chat_id="")
    chat_id, detail = await client.get_latest_chat_id()
    if not chat_id:
        return {"success": False, "chat_id": None, "message": detail}

    return {"success": True, "chat_id": chat_id, "message": detail}


@router.post(
    "/telegram/test",
    response_model=TelegramResponse,
    summary="Probar conexión con Telegram Bot",
    description="Envía un mensaje de prueba al chat indicado para validar que el Bot Token y Chat ID sean correctos.",
)
async def test_telegram(
    payload: TelegramTestRequest,
    settings: Settings = Depends(get_settings),
) -> TelegramResponse:
    """Valida y prueba las credenciales de Telegram enviando un mensaje de bienvenida."""
    token = (payload.bot_token or settings.telegram_bot_token).strip()
    chat_id = (payload.chat_id or settings.telegram_chat_id).strip()

    if not token or not chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere Bot Token y Chat ID (proporcionados en la petición o en la configuración).",
        )

    client = TelegramClient(bot_token=token, chat_id=chat_id)
    success, msg = await client.test_connection()
    return TelegramResponse(success=success, message=msg)


@router.post(
    "/telegram/send",
    response_model=TelegramResponse,
    summary="Despachar alerta a Telegram",
    description="Envía una alerta de liquidación formateada a través del bot de Telegram.",
)
async def send_telegram_alert(
    payload: TelegramSendAlertRequest,
    settings: Settings = Depends(get_settings),
) -> TelegramResponse:
    """Despacha una alerta formateada al canal de Telegram configurado."""
    token = (payload.bot_token or settings.telegram_bot_token).strip()
    chat_id = (payload.chat_id or settings.telegram_chat_id).strip()

    if not token or not chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere Bot Token y Chat ID configurados.",
        )

    client = TelegramClient(bot_token=token, chat_id=chat_id)
    success, msg = await client.send_liquidation_alert(
        title=payload.title,
        symbol=payload.symbol,
        price=payload.price,
        delta_pct=payload.delta_pct,
        volume_usd=payload.volume_usd,
        leverage=payload.leverage,
        side=payload.side,
        tactical_tip=payload.tactical_tip,
    )
    return TelegramResponse(success=success, message=msg)
