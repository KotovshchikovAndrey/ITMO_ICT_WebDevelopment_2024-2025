import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ISignInRequest, ISignUpRequest } from './types';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly baseUrl: string = 'http://127.0.0.1:8000/auth';

  constructor(private readonly http: HttpClient) {}

  signUp(data: ISignUpRequest) {
    const url = `${this.baseUrl}/users/`;
    return this.http.post<void>(url, data);
  }

  signIn(data: ISignInRequest) {
    const url = `${this.baseUrl}/token/login/`;
    return this.http
      .post<{ auth_token: string }>(url, data)
      .pipe(
        tap((response) => localStorage.setItem('token', response.auth_token))
      );
  }
}
