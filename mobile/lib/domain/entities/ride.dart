class Ride {
  final String id;
  final String driverId;
  final String origin;
  final String destination;
  final double price;
  final DateTime departureTime;

  Ride({
    required this.id,
    required this.driverId,
    required this.origin,
    required this.destination,
    required this.price,
    required this.departureTime,
  });
}
