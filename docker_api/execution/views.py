import traceback
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import CodeExecutionSerializer, RegisterSerializer
from .docker_runner import run_code_in_docker, install_package_in_docker
from .models import PythonVersion

class ExecuteCodeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        print("Authenticated user:", request.user)

        # ДО сериализации проверяем версию языка
        python_version = request.data.get("language")

        if not PythonVersion.objects.filter(version=python_version, is_active=True).exists():
            return Response(
                {"error": "Unsupported or inactive Python version"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Всё ок — продолжаем
        serializer = CodeExecutionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            code_execution = serializer.save()

            output, execution_time = run_code_in_docker(code_execution.language, code_execution.code)
            code_execution.output = output
            code_execution.execution_time = execution_time
            code_execution.status = "completed"
            code_execution.save()

            return Response(CodeExecutionSerializer(code_execution).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InstallPackageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            package = request.data.get("package")
            python_version = request.data.get("language")

            if not package:
                return Response({"error": "Package name is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка через базу данных
            if not PythonVersion.objects.filter(version=python_version, is_active=True).exists():
                return Response({"error": "Unsupported or inactive Python version"}, status=status.HTTP_400_BAD_REQUEST)

            final_message, success = install_package_in_docker(python_version, package)

            if success:
                return Response({
                    "message": final_message,
                    "status": "success"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": final_message,
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_log = traceback.format_exc()
            return Response({"error": str(e), "traceback": error_log}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PythonVersionListView(APIView):
    permission_classes = [AllowAny]  # Это открытый эндпоинт
    authentication_classes = []
    def get(self, request):
            versions = PythonVersion.objects.filter(is_active=True).values_list('version', flat=True)
            return Response({"versions": list(versions)})

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)