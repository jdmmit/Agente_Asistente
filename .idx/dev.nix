# Documentación de Nix: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }:
{
  # Canal de paquetes de Nix a utilizar.
  channel = "stable-24.05"; # También puedes usar "unstable"

  # Activar el servicio de Docker, requisito para nuestro docker-compose.
  services.docker.enable = true;

  # Paquetes de Nix disponibles en el entorno.
  # Descomenta los que necesites o busca más en https://search.nixos.org/packages
  packages = [
    pkgs.docker-compose # Esencial para orquestar nuestros servicios
  ];

  # Variables de entorno globales.
  env = {};

  # Configuración específica del IDE (IDX).
  idx = {
    # Extensiones de VS Code a instalar. Búscalas en https://open-vsx.org/
    extensions = [
      "ms-azuretools.vscode-docker" # Extensión de Docker para una mejor integración
    ];

    # Configuración de las previsualizaciones.
    previews = {
      enable = true;
      previews = [
        {
          # Nombre de la previsualización que se mostrará en el IDE.
          id = "web-app";
          # Título de la pestaña.
          label = "Memorae Web";
          # Puerto que debe exponer la previsualización.
          port = 8501;
          # Acción a realizar cuando se abre esta previsualización.
          # En este caso, no se necesita un comando aquí porque los servicios
          # ya se inician con el hook onStart.
          command = []; 
        }
      ];
    };

    # Hooks del ciclo de vida del espacio de trabajo.
    workspace = {
      # Se ejecuta cuando el espacio de trabajo se crea por primera vez.
      onCreate = {
        # Podríamos pre-cargar modelos de Ollama aquí si fuera necesario.
        # setup = "echo 'Configuración inicial completa'";
      };

      # Se ejecuta cada vez que el espacio de trabajo se inicia o reinicia.
      onStart = {
        # Levanta todos los servicios definidos en docker-compose.yml en segundo plano.
        # La bandera -d (detached) es crucial para que no bloquee el terminal.
        # --wait asegura que el comando espera a que los servicios estén saludables.
        start-services = "docker compose up -d --wait";
      };
    };
  };
}
