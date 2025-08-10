from drf_spectacular.utils import OpenApiParameter

public_event_id_parameter = OpenApiParameter(
    name="event_public_id",
    type=str,
    location="path",
    description="The public ID of the event",
)
public_ticket_id_parameter = OpenApiParameter(
    name="ticket_public_id",
    type=str,
    location="path",
    description="The public ID of the ticket",
)
