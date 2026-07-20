import 'package:flutter/material.dart';

class ApuraditoButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isOutlined;
  final Color? color;
  final Widget? icon;

  const ApuraditoButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.isOutlined = false,
    this.color,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    // We assume AppTheme is available, if not we will use standard colors for now.
    // The prompt says: AppTheme.primary = #7C3AED
    const primaryColor = Color(0xFF7C3AED);

    final buttonStyle = ElevatedButton.styleFrom(
      backgroundColor: Colors.transparent,
      shadowColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.0), // radiusMd
      ),
      padding: EdgeInsets.zero,
    );

    final content = isLoading
        ? const Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2.5,
              ),
            ),
          )
        : Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                icon!,
                const SizedBox(width: 8),
              ],
              Text(
                text,
                style: TextStyle(
                  color: isOutlined ? primaryColor : Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          );

    return Container(
      height: 52.0,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8.0),
        gradient: !isOutlined && onPressed != null
            ? const LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFF9F67FF)],
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
              )
            : null,
        color: isOutlined ? Colors.transparent : (onPressed == null ? Colors.grey : null),
        border: isOutlined
            ? Border.all(color: primaryColor, width: 2)
            : null,
        boxShadow: !isOutlined && onPressed != null
            ? [
                BoxShadow(
                  color: primaryColor.withOpacity(0.4),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ]
            : [],
      ),
      child: ElevatedButton(
        style: buttonStyle,
        onPressed: isLoading ? null : onPressed,
        child: content,
      ),
    );
  }
}
