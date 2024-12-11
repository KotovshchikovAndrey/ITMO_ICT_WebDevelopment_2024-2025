export interface ISignUpRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface ISignInRequest {
  email: string;
  password: string;
}
