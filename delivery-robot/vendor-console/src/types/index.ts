export type OrderStatus =
  | "NEW"
  | "ACCEPTED"
  | "PREPARING"
  | "READY"
  | "REJECTED";

export interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  customisation?: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  studentName: string;
  deliveryLocation: string;
  items: OrderItem[];
  status: OrderStatus;
  createdAt: Date;
  updatedAt: Date;
}
