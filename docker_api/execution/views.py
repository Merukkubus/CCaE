import traceback
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import CodeExecutionSerializer, RegisterSerializer
from .docker_runner import run_code_generic, install_package_in_docker
from .models import CodeExecution, Subscription, UserProfile, LanguageVersion, Language


class ExecuteCodeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        print("Authenticated user:", request.user)
        print("Payload received:", request.data)

        language_name = request.data.get("language")
        version = request.data.get("version")
        code = request.data.get("code")
        libs_raw = request.data.get("libs", "")
        libs = [lib.strip() for lib in libs_raw.split(",") if lib.strip()]

        try:
            lang = Language.objects.get(name=language_name)
            lang_version = lang.versions.get(version=version, is_active=True)
        except Language.DoesNotExist:
            return Response({"error": "Unsupported language"}, status=400)
        except LanguageVersion.DoesNotExist:
            return Response({"error": "Unsupported or inactive version"}, status=400)

        # Подготовка данных для сериализатора
        data = request.data.copy()
        data['language_version'] = lang_version.id  # <-- ключевая строка

        serializer = CodeExecutionSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            code_execution = serializer.save()

            docker_name = lang.docker_name.lower()
            docker_image = f"{docker_name}:{version}"

            if docker_name == "python":
                run_cmd = "python3 /tmp/main.txt"
                file_ext = "txt"
                compile_cmd = None
            elif docker_name == "gcc":
                compile_cmd = "g++ -fno-diagnostics-color /tmp/main.cpp -o /tmp/a.out"
                run_cmd = "/tmp/a.out"
                file_ext = "cpp"
            else:
                return Response({"error": f"Language '{lang.name}' not supported yet"}, status=400)

            output, execution_time = run_code_generic(
                language=lang.name,
                version=version,
                code=code,
                compile_cmd=compile_cmd,
                run_cmd=run_cmd,
                libs=libs,
                file_ext=file_ext,
                docker_image=docker_image
            )

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
            language_name = request.data.get("language")
            version = request.data.get("version")

            if not package:
                return Response({"error": "Package name is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                lang = Language.objects.get(name=language_name)
                lang_version = lang.versions.get(version=version, is_active=True)
            except Language.DoesNotExist:
                return Response({"error": "Unsupported language"}, status=400)
            except LanguageVersion.DoesNotExist:
                return Response({"error": "Unsupported or inactive version"}, status=400)

            if lang.name.lower() != "python":
                return Response({"error": "Package installation only supported for Python"}, status=400)

            final_message, success = install_package_in_docker(version, package)

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


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableLanguagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        result = {}
        for lang in Language.objects.all():
            active_versions = lang.versions.filter(is_active=True).values_list('version', flat=True)
            result[lang.name] = list(active_versions)
        return Response({"languages": result})