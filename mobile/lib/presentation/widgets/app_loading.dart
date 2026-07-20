import 'package:flutter/material.dart';

class AppLoadingOverlay extends StatelessWidget {
  final Widget child;
  final bool isLoading;

  const AppLoadingOverlay({
    super.key,
    required this.child,
    required this.isLoading,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Container(
            color: Colors.black.withOpacity(0.5),
            child: const Center(
              child: CircularProgressIndicator(
                color: Color(0xFF7C3AED),
              ),
            ),
          ),
      ],
    );
  }
}

class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String text;

  const AppEmptyState({
    super.key,
    required this.icon,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          Text(
            text,
            style: const TextStyle(color: Colors.white70, fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
