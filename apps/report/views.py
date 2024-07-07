from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .enums import Status
from apps.mailer import generic_sender as Mailer
from rest_framework import status

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_reports(request):
        reports = Report.objects.filter(user_id=request.user.id)
        if not reports:
            return Response({'message': 'The user has no reports'}, status=status.HTTP_404_NOT_FOUND)
        reports_serializer = ReportSerializer(reports, many=True)
        return Response(reports_serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_report_create(request) -> Response:
    datos = request.data.copy()
    datos['user'] = request.user.id
    datos['status'] = Status.PENDIENTE
    datos['created_at'] = datetime.now()

    serializer = ReportSerializer(data=datos)
    
    if serializer.is_valid():
        report = serializer.save()
        report.save()
        user = report.user
        Mailer.send_email(
            subject="AparKing - Confirmación de incidencia",
            message=f"Hola {user.first_name}, te enviamos este correo para confirmar que la incidencia '{report.title}' ha sido registrada con éxito.\n\nEn breves momentos nos pondremos en contacto contigo para solucionarla.\n\nGracias por confiar en nosotros.",
            mail_to=user.email,
        )
        return Response(status=200)
    else:
        return Response(serializer.errors, status=400)