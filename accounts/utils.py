from django.db.models import Case, When, F, ExpressionWrapper, FloatField, IntegerField
from django.db.models.functions import ASin, Sqrt, Cos, Sin, Radians, Power, ACos

def get_haversine_expression(lat, lng, prefix=''):
    """
    Returns an expression to calculate distance in km using Haversine
    """
    lat_field = f"{prefix}location_lat"
    lng_field = f"{prefix}location_lng"

    # Haversine formula
    # 6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians(lat2)))

    return ExpressionWrapper(
        6371 * ACos(
            Cos(Radians(lat)) * Cos(Radians(F(lat_field))) *
            Cos(Radians(F(lng_field)) - Radians(lng)) +
            Sin(Radians(lat)) * Sin(Radians(F(lat_field)))
        ),
        output_field=FloatField()
    )

def similarity_score(user, prefix=''):
    """
    Returns an expression to calculate similarity score
    """
    fields_to_check = [
        ('city', 30),
        ('seeking', 20),
        ('lifestyle', 15),
        ('marital_status', 15),
        ('style', 10),
        ('health_status', 10)
    ]

    cases = []
    for field, weight in fields_to_check:
        val = getattr(user, field)
        if val is not None:
            cases.append(
                Case(
                    When(**{f"{prefix}{field}": val}, then=weight),
                    default=0,
                    output_field=IntegerField()
                )
            )

    if cases:
        expression = cases[0]
        for c in cases[1:]:
            expression += c
        return ExpressionWrapper(expression, output_field=IntegerField())
    return ExpressionWrapper(0, output_field=IntegerField())
