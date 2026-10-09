import 'package:flutter/material.dart';
import 'screens/web_platform_screen.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const OfertappApp());
}

class OfertappApp extends StatelessWidget {
  const OfertappApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ofertapp',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const WebPlatformScreen(),
    );
  }
}
