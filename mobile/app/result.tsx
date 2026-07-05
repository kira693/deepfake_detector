import ResultScreen from '../src/screens/ResultScreen';
import { useLocalSearchParams, useRouter } from 'expo-router';

export default function Result() {
  const params = useLocalSearchParams();
  const router = useRouter();
  
  let result = null;
  try {
    result = params.result ? JSON.parse(params.result as string) : null;
  } catch (e) {
    result = null;
  }

  if (!result) {
    return null;
  }

  const navigation = {
    navigate: (screen: string) => router.push(`/${screen.toLowerCase()}` as any)
  };

  return <ResultScreen route={{ params: { result } }} navigation={navigation} />;
}