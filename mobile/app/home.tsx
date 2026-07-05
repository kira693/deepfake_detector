import HomeScreen from '../src/screens/HomeScreen';
import { useRouter } from 'expo-router';

export default function Home() {
  const router = useRouter();
  const navigation = {
    navigate: (screen: string, params?: any) => {
      router.push({
        pathname: `/${screen.toLowerCase()}` as any,
        params: { result: params?.result }
      });
    }
  };
  return <HomeScreen navigation={navigation} />;
}