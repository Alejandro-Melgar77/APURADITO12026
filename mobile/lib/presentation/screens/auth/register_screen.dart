import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/widgets/apuradito_button.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _nombreController = TextEditingController();
  final TextEditingController _apellidoController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _telefonoController = TextEditingController();
  final TextEditingController _ciController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();
  final TextEditingController _placaController = TextEditingController();
  final TextEditingController _marcaController = TextEditingController();
  final TextEditingController _modeloController = TextEditingController();
  final TextEditingController _colorController = TextEditingController();
  final TextEditingController _anioController = TextEditingController();
  final TextEditingController _asientosController =
      TextEditingController(text: '5');

  String _selectedRol = 'pasajero';
  DateTime? _fechaNacimiento;

  bool get _isDriver => _selectedRol == 'conductor';

  @override
  void dispose() {
    _nombreController.dispose();
    _apellidoController.dispose();
    _emailController.dispose();
    _telefonoController.dispose();
    _ciController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _placaController.dispose();
    _marcaController.dispose();
    _modeloController.dispose();
    _colorController.dispose();
    _anioController.dispose();
    _asientosController.dispose();
    super.dispose();
  }

  Future<void> _selectBirthDate() async {
    final DateTime now = DateTime.now();
    final DateTime? selected = await showDatePicker(
      context: context,
      initialDate: _fechaNacimiento ?? DateTime(now.year - 21),
      firstDate: DateTime(now.year - 100),
      lastDate: DateTime(now.year - 18),
    );
    if (selected != null) setState(() => _fechaNacimiento = selected);
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    if (_isDriver && _fechaNacimiento == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecciona tu fecha de nacimiento.')),
      );
      return;
    }

    final AuthProvider auth = context.read<AuthProvider>();
    final bool success = await auth.register(
      email: _emailController.text,
      password: _passwordController.text,
      nombre: _nombreController.text,
      apellido: _apellidoController.text,
      ci: _ciController.text,
      telefono: _telefonoController.text,
      rol: _selectedRol,
      fechaNacimiento: _fechaNacimiento,
      placa: _placaController.text,
      marca: _marcaController.text,
      modelo: _modeloController.text,
      color: _colorController.text,
      anioVehiculo: int.tryParse(_anioController.text),
      asientosTotales: int.tryParse(_asientosController.text),
    );
    if (!mounted) return;

    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(auth.errorMessage ?? 'No se pudo crear la cuenta')),
      );
      return;
    }

    if (auth.registrationPendingApproval) {
      await showDialog<void>(
        context: context,
        builder: (BuildContext dialogContext) => AlertDialog(
          title: const Text('Registro enviado'),
          content: const Text(
            'Tu cuenta de conductor necesita validar identidad y vehiculo antes de publicar rutas. Te avisaremos al activarla.',
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Entendido'),
            ),
          ],
        ),
      );
      if (mounted) context.go('/login');
      return;
    }
    context.go('/passenger');
  }

  @override
  Widget build(BuildContext context) {
    final bool isLoading = context.watch<AuthProvider>().isLoading;
    return Scaffold(
      backgroundColor: const Color(0xFF0F0A1E),
      appBar: AppBar(title: const Text('Crear cuenta')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text('Elige como usaras Apuradito',
                    style: TextStyle(color: Colors.white70)),
                const SizedBox(height: 16),
                Row(
                  children: <Widget>[
                    _RoleCard(
                      selected: !_isDriver,
                      icon: Icons.person,
                      label: 'Pasajero',
                      onTap: () => setState(() => _selectedRol = 'pasajero'),
                    ),
                    const SizedBox(width: 12),
                    _RoleCard(
                      selected: _isDriver,
                      icon: Icons.directions_car,
                      label: 'Conductor',
                      onTap: () => setState(() => _selectedRol = 'conductor'),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _field(_nombreController, 'Nombre', Icons.person),
                _field(_apellidoController, 'Apellido', Icons.person_outline),
                _field(_emailController, 'Correo electronico', Icons.email,
                    keyboardType: TextInputType.emailAddress,
                    validator: (String? value) {
                  if (value == null || !value.contains('@')) {
                    return 'Ingresa un correo valido';
                  }
                  return null;
                }),
                _field(_telefonoController, 'Telefono', Icons.phone,
                    keyboardType: TextInputType.phone),
                _field(_ciController, 'CI / Carnet', Icons.badge,
                    validator: (String? value) {
                  if (_isDriver && (value == null || value.trim().isEmpty)) {
                    return 'El carnet es obligatorio para conductores';
                  }
                  return null;
                }),
                if (_isDriver) ...<Widget>[
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _selectBirthDate,
                    icon: const Icon(Icons.cake_outlined),
                    label: Text(_fechaNacimiento == null
                        ? 'Fecha de nacimiento'
                        : 'Nacimiento: ${_fechaNacimiento!.day.toString().padLeft(2, '0')}/${_fechaNacimiento!.month.toString().padLeft(2, '0')}/${_fechaNacimiento!.year}'),
                  ),
                  const SizedBox(height: 20),
                  const Text('Datos del vehiculo',
                      style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold)),
                  _field(_placaController, 'Placa', Icons.pin,
                      validator: _requiredDriverField),
                  _field(_marcaController, 'Marca', Icons.directions_car,
                      validator: _requiredDriverField),
                  _field(_modeloController, 'Modelo', Icons.sell_outlined,
                      validator: _requiredDriverField),
                  _field(_colorController, 'Color', Icons.palette_outlined,
                      validator: _requiredDriverField),
                  _field(
                      _anioController, 'Año del vehiculo', Icons.calendar_today,
                      keyboardType: TextInputType.number,
                      validator: _vehicleYearValidator),
                  _field(
                      _asientosController, 'Asientos totales', Icons.event_seat,
                      keyboardType: TextInputType.number,
                      validator: _seatsValidator),
                  const Padding(
                    padding: EdgeInsets.only(top: 4),
                    child: Text(
                      'La cuenta de conductor queda pendiente hasta verificar identidad y vehiculo.',
                      style: TextStyle(color: Colors.white60),
                    ),
                  ),
                ],
                _field(_passwordController, 'Contraseña', Icons.lock,
                    obscureText: true, validator: (String? value) {
                  if (value == null || value.length < 6) {
                    return 'Usa al menos 6 caracteres';
                  }
                  return null;
                }),
                _field(_confirmPasswordController, 'Confirmar contraseña',
                    Icons.lock_outline, obscureText: true,
                    validator: (String? value) {
                  if (value != _passwordController.text) {
                    return 'Las contraseñas no coinciden';
                  }
                  return null;
                }),
                const SizedBox(height: 24),
                ApuraditoButton(
                  text: 'Crear cuenta',
                  isLoading: isLoading,
                  onPressed: _register,
                ),
                Center(
                  child: TextButton(
                    onPressed: () => context.pop(),
                    child: const Text('Ya tengo una cuenta'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(
    TextEditingController controller,
    String label,
    IconData icon, {
    TextInputType? keyboardType,
    bool obscureText = false,
    String? Function(String?)? validator,
  }) =>
      Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          obscureText: obscureText,
          decoration: InputDecoration(labelText: label, prefixIcon: Icon(icon)),
          validator: validator ??
              (String? value) => value == null || value.trim().isEmpty
                  ? 'Campo obligatorio'
                  : null,
        ),
      );

  String? _requiredDriverField(String? value) =>
      _isDriver && (value == null || value.trim().isEmpty)
          ? 'Campo obligatorio para conductores'
          : null;

  String? _vehicleYearValidator(String? value) {
    final int? year = int.tryParse(value ?? '');
    if (year == null || year < 1950 || year > DateTime.now().year + 1) {
      return 'Ingresa un año valido';
    }
    return null;
  }

  String? _seatsValidator(String? value) {
    final int? seats = int.tryParse(value ?? '');
    if (seats == null || seats < 2 || seats > 60) {
      return 'Ingresa entre 2 y 60 asientos';
    }
    return null;
  }
}

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.selected,
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final bool selected;
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Expanded(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color:
                  selected ? const Color(0xFF7C3AED) : const Color(0xFF1A1035),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: <Widget>[
                Icon(icon, color: Colors.white),
                const SizedBox(height: 6),
                Text(label, style: const TextStyle(color: Colors.white)),
              ],
            ),
          ),
        ),
      );
}
