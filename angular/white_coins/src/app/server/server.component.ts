import { Component } from '@angular/core';

@Component({
  selector: 'app-server',
  templateUrl: './server.component.html',
  styles: [`
    .online {
      color: white;
    }
  `]
})
export class ServerComponent {
  transId: number = 10;
  serverStatus: string = 'malicious';

  constructor() {
    this.serverStatus = Math.random() > 0.5 ? 'good' : 'malicious';
  }

  getTransactionStatus() {
    return this.serverStatus;
  }

  getColor() {
    return this.serverStatus === 'good' ? 'green' : 'red';
  }
}
