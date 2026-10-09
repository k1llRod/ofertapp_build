import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
// Para configuraciones específicas de Android WebView si están disponibles
import 'package:webview_flutter_android/webview_flutter_android.dart';

class WebPlatformScreen extends StatefulWidget {
  const WebPlatformScreen({super.key});

  @override
  State<WebPlatformScreen> createState() => _WebPlatformScreenState();
}

class _WebPlatformScreenState extends State<WebPlatformScreen> {
  late final WebViewController _controller;
  double _progress = 0;
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';

  // IP por defecto del Gateway en la red local actual
  String _serverUrl = 'http://192.168.1.210:8000/app';

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  void _initWebView() {
    final PlatformWebViewControllerCreationParams params;
    if (WebViewPlatform.instance is AndroidWebViewPlatform) {
      params = AndroidWebViewControllerCreationParams();
    } else {
      params = const PlatformWebViewControllerCreationParams();
    }

    final WebViewController controller =
        WebViewController.fromPlatformCreationParams(params);

    controller
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF0F172A))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            setState(() {
              _progress = progress / 100.0;
            });
          },
          onPageStarted: (String url) {
            setState(() {
              _isLoading = true;
              _hasError = false;
            });
          },
          onPageFinished: (String url) {
            setState(() {
              _isLoading = false;
            });
          },
          onWebResourceError: (WebResourceError error) {
            // Solo registrar error si es sobre la página principal
            if (error.isForMainFrame ?? true) {
              setState(() {
                _isLoading = false;
                _hasError = true;
                _errorMessage = error.description;
              });
            }
          },
        ),
      );

    if (controller.platform is AndroidWebViewController) {
      final androidController = controller.platform as AndroidWebViewController;
      androidController.setGeolocationPermissionsPromptCallbacks(
        onShowPrompt: (request) async {
          return const GeolocationPermissionsResponse(
            allow: true,
            retain: true,
          );
        },
      );
    }

    controller.loadRequest(Uri.parse(_serverUrl));
    _controller = controller;
  }

  Future<void> _changeServerDialog() async {
    final textController = TextEditingController(text: _serverUrl);
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Configurar Servidor Ofertapp'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ingresa la URL o IP del API Gateway donde corren los microservicios:',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: textController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'http://192.168.1.210:8000/app',
                labelText: 'URL del Gateway',
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                ActionChip(
                  label: const Text('IP Actual (210)'),
                  onPressed: () {
                    textController.text = 'http://192.168.1.210:8000/app';
                  },
                ),
                ActionChip(
                  label: const Text('Emulador (10.0.2.2)'),
                  onPressed: () {
                    textController.text = 'http://10.0.2.2:8000/app';
                  },
                ),
                ActionChip(
                  label: const Text('Localhost'),
                  onPressed: () {
                    textController.text = 'http://127.0.0.1:8000/app';
                  },
                ),
              ],
            )
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, textController.text.trim()),
            child: const Text('Conectar'),
          ),
        ],
      ),
    );

    if (result != null && result.isNotEmpty && result != _serverUrl) {
      setState(() {
        _serverUrl = result;
        _isLoading = true;
        _hasError = false;
      });
      _controller.loadRequest(Uri.parse(_serverUrl));
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (await _controller.canGoBack()) {
          await _controller.goBack();
        } else {
          if (context.mounted) {
            Navigator.of(context).maybePop();
          }
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        body: SafeArea(
          child: Stack(
            children: [
              if (!_hasError)
                WebViewWidget(controller: _controller),

              if (_isLoading && !_hasError)
                Positioned(
                  top: 0,
                  left: 0,
                  right: 0,
                  child: LinearProgressIndicator(
                    value: _progress > 0 ? _progress : null,
                    color: const Color(0xFFF59E0B),
                    backgroundColor: Colors.transparent,
                  ),
                ),

              if (_hasError)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 28),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.amber.shade50,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.wifi_off_rounded,
                            size: 54,
                            color: Colors.amber.shade800,
                          ),
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          'No se pudo conectar a Ofertapp',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Servidor: $_serverUrl\n\nAsegúrate de que la PC y tu dispositivo móvil estén conectados a la misma red Wi-Fi y los microservicios estén levantados.',
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 13,
                            color: Color(0xFF64748B),
                            height: 1.4,
                          ),
                        ),
                        if (_errorMessage.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Text(
                            'Detalle: $_errorMessage',
                            style: const TextStyle(
                              fontSize: 11,
                              color: Colors.redAccent,
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            OutlinedButton.icon(
                              onPressed: _changeServerDialog,
                              icon: const Icon(Icons.settings, size: 18),
                              label: const Text('Cambiar IP'),
                            ),
                            const SizedBox(width: 12),
                            ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFF59E0B),
                                foregroundColor: Colors.black,
                              ),
                              onPressed: () {
                                setState(() {
                                  _isLoading = true;
                                  _hasError = false;
                                });
                                _controller.loadRequest(Uri.parse(_serverUrl));
                              },
                              icon: const Icon(Icons.refresh, size: 18),
                              label: const Text('Reintentar'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),

              // Botón flotante discreto en esquina inferior para opciones de testing/servidor
              Positioned(
                bottom: 12,
                right: 12,
                child: Opacity(
                  opacity: 0.85,
                  child: FloatingActionButton.small(
                    heroTag: 'config_server_btn',
                    backgroundColor: const Color(0xFF1E293B),
                    foregroundColor: Colors.white,
                    tooltip: 'Opciones de Servidor / Testing',
                    onPressed: _changeServerDialog,
                    child: const Icon(Icons.tune, size: 18),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
